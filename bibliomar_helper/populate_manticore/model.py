from pydantic import BaseModel, BaseSettings, Field

md5_reg = "^[0-9a-fA-F]{32}$"


class MYSQLCredentials(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASS: str
    MYSQL_DB: str


class MEILICredentials(BaseSettings):
    MEILI_URL: str
    MEILI_MASTER_KEY: str | None


class SearchEntry(BaseModel):
    authors: str
    title: str
    md5: str = Field(..., regex=md5_reg)
    topic: str
    extension: str
    size: str
    language: str | None
    cover_url: str | None
