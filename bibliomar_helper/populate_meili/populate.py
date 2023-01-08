import os
from bibliomar_helper.populate_meili.config import (
    connect_to_meili,
    connect_to_mysql,
    get_environ_limit,
)
from bibliomar_helper.populate_meili.helper import (
    get_current_offset,
    results_to_entries,
    save_current_offset,
)


def populate_meilisearch(topic: str):
    get_offset = get_current_offset()
    offset = get_offset[topic]
    limit = get_environ_limit()

    meili_client = connect_to_meili()
    meili_index = meili_client.index("books")
    conn = connect_to_mysql()
    cursor = conn.cursor()

    table = topic if topic == "fiction" else "updated"
    # 10 minutes in milliseconds
    max_wait_timeout = 10 * 60 * 1000

    while True:

        # Remove on prod
        # if offset >= 500000:
        #     print("Limiting in dev environment")
        #     break

        sql = f"""
        SELECT * FROM {table} LIMIT %s OFFSET %s
        """

        print(f"Using offset: {offset} for table {table}")
        cursor.execute(sql, (limit, offset))
        results = cursor.fetchall()
        print("SQL query done.")
        results_as_models = results_to_entries(topic, results)
        print(f"Using {len(results_as_models)} of {len(results)} results.")
        task = meili_index.add_documents(results_as_models)
        task_id = task.task_uid
        print("Waiting for task: ", task_id)
        meili_index.wait_for_task(task_id, timeout_in_ms=max_wait_timeout)
        print("Task done: ", task_id)
        offset += limit
        if results is None or len(results) < limit:
            break
        print("Saving current offset...")
        save_current_offset(topic, offset)

    conn.close()
