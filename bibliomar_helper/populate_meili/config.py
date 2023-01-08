from genericpath import isfile
import json
from dotenv import load_dotenv
from pymysql import connect
from pymysql.cursors import DictCursor
from meilisearch import Client
from sqlite3 import Connection, connect as sqlite_connect

from bibliomar_helper.populate_meili.model import (
    MYSQLCredentials,
    MEILICredentials,
)

import os

search_limit = 500000

load_dotenv()
mysql_credentials = MYSQLCredentials()  # type: ignore
meili_credentials = MEILICredentials()  # type: ignore


def configure_sqlite(conn: Connection):
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS offset (
        fiction INTEGER, scitech INTEGER, date DATETIME DEFAULT CURRENT_TIMESTAMP)"""
    )
    cursor.execute("SELECT * FROM offset LIMIT 1")
    req = cursor.fetchone()
    if req is None or len(req) == 0:
        cursor.execute("INSERT INTO offset (fiction, scitech) VALUES (0, 0)")


def connect_to_sqlite():
    conn = sqlite_connect("populate.db")
    configure_sqlite(conn)
    return conn


def connect_to_mysql():
    conn = connect(
        host=mysql_credentials.MYSQL_HOST,
        user=mysql_credentials.MYSQL_USER,
        password=mysql_credentials.MYSQL_PASS,
        db=mysql_credentials.MYSQL_DB,
        cursorclass=DictCursor,
    )
    conn.ping(reconnect=True)
    return conn


def configure_meili(client: Client):
    client.create_index("books", {"primaryKey": "md5"})
    client.index("books").update_filterable_attributes(
        ["authors", "title", "topic", "extension", "language"]
    )


def connect_to_meili():
    credentials = meili_credentials
    client = Client(credentials.MEILI_URL)
    configure_meili(client)
    return client
