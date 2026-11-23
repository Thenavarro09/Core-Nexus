from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / "config.env"


class Settings(BaseSettings):
    sql_server: str = "localhost"
    sql_port: int = 1433
    sql_database: str = "master"
    sql_auth: Literal["windows", "sql"] = "windows"
    sql_user: str = ""
    sql_password: str = ""
    sql_driver: str = "ODBC Driver 18 for SQL Server"
    sql_trust_server_certificate: bool = True

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
