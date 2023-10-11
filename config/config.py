from typing import Any, Dict, Optional, Union
from pydantic import BaseSettings, PostgresDsn, validator


SENTRY_DSN_TEST = ""


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "async_python_sprint_3"
    DB_PORT: str = 5432
    DB_URL: Optional[Union[PostgresDsn, str]] = ""

    TEST_DB_HOST: str = "localhost"
    TEST_DB_USER: str = "postgres"
    TEST_DB_PASSWORD: str = "postgres"
    TEST_DB_NAME: str = "test_async_python_sprint_3"
    TEST_DB_PORT: str = "5432"
    TEST_DB_URL: Optional[Union[PostgresDsn, str]] = ""

    ROOT_DIR: str = ""

    @validator("DB_URL", pre=True)
    def assemble_db_connection(cls, value: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(value, str) and value != "":
            return value

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    @validator("TEST_DB_URL", pre=True)
    def assemble_test_db_connection(cls, value: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(value, str) and value != "":
            return value

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("TEST_DB_USER"),
            password=values.get("TEST_DB_PASSWORD"),
            host=values.get("TEST_DB_HOST"),
            port=values.get("TEST_DB_PORT"),
            path=f"/{values.get('TEST_DB_NAME') or ''}",
        )

settings = Settings()
