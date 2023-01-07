from pydantic import BaseSettings


class MYSQLCredentials(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASS: str
    MYSQL_DB: str


class MEILICredentials(BaseSettings):
    MEILI_URL: str
