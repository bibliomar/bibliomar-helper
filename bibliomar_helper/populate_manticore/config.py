from genericpath import isfile
import json
from typing import Optional
from dotenv import load_dotenv
from pymysql import connect
from pymysql.cursors import DictCursor
from meilisearch import Client
from sqlite3 import Connection, connect as sqlite_connect
import manticoresearch

from bibliomar_helper.populate_meili.model import (
    MANTICORECredentials,
    MYSQLCredentials,
    MEILICredentials,
)

import os

load_dotenv()
mysql_credentials = MYSQLCredentials()  # type: ignore
manticore_credentials = MANTICORECredentials()  # type: ignore


def get_environ_limit():
    environ_limit = os.environ.get("POPULATE_LIMIT")
    if environ_limit is None or environ_limit == "":
        return 10000
    else:
        return int(environ_limit)


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


def configure_manticore(utilsApi: manticoresearch.UtilsApi):
    utilsApi.sql(
        """CREATE TABLE IF NOT EXISTS books (id bigint, title text, 
                 authors text, 
                 topic text, 
                 extension text, 
                 language text, 
                 MD5 string)
                 """
    )


def connect_to_manticore() -> manticoresearch.ApiClient:
    config = manticoresearch.Configuration(host=manticore_credentials.MANTICORE_URL)

    client = manticoresearch.ApiClient(config)
    utilsApi = manticoresearch.UtilsApi(client)
    configure_manticore(utilsApi)

    return client
