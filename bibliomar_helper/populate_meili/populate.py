from json import JSONDecodeError
import os
import time
from typing import Optional
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

conn = connect_to_mysql()
meili_client = connect_to_meili()


def populate_meilisearch(topic: str):
    get_offset = get_current_offset()
    offset = get_offset[topic]
    limit = get_environ_limit()

    meili_index = meili_client.index("books")

    cursor = conn.cursor()

    table = topic if topic == "fiction" else "updated"
    # 10 minutes in milliseconds
    max_wait_timeout = 10 * 60 * 1000

    while True:

        health = meili_client.health()
        if health["status"] != "available":
            print("MeiliSearch is not available. Waiting for 30 seconds...")
            time.sleep(60)
            continue

        sql = f"""
        SELECT * FROM {table} LIMIT %s OFFSET %s
        """

        print(f"Using offset: {offset} for table {table}")
        cursor.execute(sql, (limit, offset))
        results = cursor.fetchall()
        print("SQL query done.")
        if results is None or len(results) < limit:
            print("No more results to process in table ." + table)
            break
        results_as_models = results_to_entries(topic, results)
        print(f"Using {len(results_as_models)} of {len(results)} results.")
        print("Starting tasks...")
        tasks = meili_index.add_documents_in_batches(results_as_models)

        while True:

            tasks_are_finished = True

            for task in tasks:
                task_id = task.task_uid
                task_info = meili_client.get_task(task_id)
                task_status = task_info["status"]

                if task_status == "enqueued" or task_status == "processing":
                    tasks_are_finished = False

                else:

                    if task_status != "succeeded":
                        print("A task has failed. Pay close attention: ")
                        print(task)

            if tasks_are_finished:
                break

            time.sleep(1)

        print(f"Finished saving books between {offset} and {offset + limit}.")
        print("Saving current offset to local database...")
        save_current_offset(topic, offset)
        # print("Waiting for 60 seconds before next batch...")
        # time.sleep(60)
        offset += limit
