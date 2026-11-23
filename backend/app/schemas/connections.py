from typing import Literal

from pydantic import BaseModel, Field


class ConnectionTestRequest(BaseModel):
    server: str = Field(min_length=1, max_length=255)
    port: int = Field(default=1433, ge=1, le=65535)
    database: str = Field(default="master", min_length=1, max_length=128)
    auth: Literal["windows", "sql"] = "windows"
    username: str = ""
    password: str = ""
    driver: str = "ODBC Driver 18 for SQL Server"
    trust_server_certificate: bool = True


class DatabaseInfo(BaseModel):
    name: str
    database_id: int
    state: str
    recovery_model: str
    create_date: str | None = None


class ConnectionTestResponse(BaseModel):
    ok: bool
    server_name: str
    version: str
    current_database: str
    databases: list[DatabaseInfo]


class DatabaseListResponse(BaseModel):
    databases: list[DatabaseInfo]
