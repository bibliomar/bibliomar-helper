from dotenv import load_dotenv
from pymysql import connect
from pymysql.cursors import DictCursor
from meilisearch import Client

from bibliomar_helper.populate_meili.model import MYSQLCredentials, MEILICredentials


load_dotenv()
mysql_credentials = MYSQLCredentials()  # type: ignore
meili_credentials = MEILICredentials()  # type: ignore


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


def connect_to_meili():
    credentials = meili_credentials
    client = Client(credentials.MEILI_URL)
    return client
