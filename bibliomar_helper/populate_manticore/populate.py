from json import JSONDecodeError
import json
import os
import time
from typing import Optional
from bibliomar_helper.populate_manticore.config import (
    connect_to_mysql,
    get_environ_limit,
    connect_to_manticore,
)
from bibliomar_helper.populate_manticore.helper import (
    build_single_manticore_request,
    get_current_offset,
    results_to_entries,
    save_current_offset,
)
import manticoresearch

mysql_conn = connect_to_mysql()
manticore_conn = connect_to_manticore()


def populate_manticore(topic: str):
    get_offset = get_current_offset()
    offset = get_offset[topic]
    limit = get_environ_limit()

    cursor = mysql_conn.cursor()
    manticore_index = manticoresearch.IndexApi(manticore_conn)
    manticore_utils = manticoresearch.UtilsApi(manticore_conn)

    table = topic if topic == "fiction" else "updated"
    # 10 minutes in milliseconds
    max_wait_timeout = 10 * 60 * 1000

    while True:

        if offset > 101:

            break

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

        for result in results_as_models:
            request = build_single_manticore_request(result)
            print(request)
            manticore_utils.sql(request)

        print(f"Finished saving books between {offset} and {offset + limit}.")
        print("Saving current offset to local database...")
        save_current_offset(topic, offset)
        # print("Waiting for 60 seconds before next batch...")
        offset += limit
