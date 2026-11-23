import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

import pyodbc

from app.core.config import Settings
from app.core.exceptions import DatabaseConnectionError

SERVER_INFO_SQL = """
SELECT
    @@SERVERNAME AS server_name,
    @@VERSION AS version,
    DB_NAME() AS current_database
"""

DATABASES_SQL = """
SELECT
    name,
    database_id,
    state_desc AS state,
    recovery_model_desc AS recovery_model,
    create_date
FROM sys.databases
ORDER BY name
"""

_CONNECT_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class ConnectionParams:
    server: str
    port: int
    database: str
    auth: Literal["windows", "sql"]
    username: str = ""
    password: str = ""
    driver: str = "ODBC Driver 18 for SQL Server"
    trust_server_certificate: bool = True


def params_from_settings(settings: Settings) -> ConnectionParams:
    return ConnectionParams(
        server=settings.sql_server,
        port=settings.sql_port,
        database=settings.sql_database or "master",
        auth=settings.sql_auth,
        username=settings.sql_user,
        password=settings.sql_password,
        driver=settings.sql_driver,
        trust_server_certificate=settings.sql_trust_server_certificate,
    )


def build_connection_string(params: ConnectionParams) -> str:
    _validate(params)
    parts = [
        f"DRIVER={_odbc_value(params.driver)}",
        f"SERVER={_odbc_value(f'{params.server},{params.port}')}",
        f"DATABASE={_odbc_value(params.database)}",
        f"Connection Timeout={_CONNECT_TIMEOUT_SECONDS}",
        (
            "TrustServerCertificate=yes"
            if params.trust_server_certificate
            else "TrustServerCertificate=no"
        ),
    ]
    if params.auth == "windows":
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={_odbc_value(params.username)}")
        parts.append(f"PWD={_odbc_value(params.password)}")
    return ";".join(parts) + ";"


def inspect_server(params: ConnectionParams) -> dict:
    """Abre una conexión, lee la versión del servidor y lista sus bases."""
    connection = _connect(params)
    try:
        info = _query(connection, SERVER_INFO_SQL)[0]
        databases = [_database_row(row) for row in _query(connection, DATABASES_SQL)]
    except pyodbc.Error as exc:
        raise translate_odbc_error(exc) from exc
    finally:
        connection.close()

    version = str(info.get("version") or "").strip()
    return {
        "ok": True,
        "server_name": info.get("server_name") or params.server,
        "version": version,
        "current_database": info.get("current_database") or params.database,
        "databases": databases,
    }


def list_databases(params: ConnectionParams) -> list[dict]:
    connection = _connect(params)
    try:
        return [_database_row(row) for row in _query(connection, DATABASES_SQL)]
    except pyodbc.Error as exc:
        raise translate_odbc_error(exc) from exc
    finally:
        connection.close()


def translate_odbc_error(exc: pyodbc.Error) -> DatabaseConnectionError:
    sqlstate = str(exc.args[0]) if exc.args else ""
    message = _public_error_text(exc)

    if "login failed" in message or "18456" in message:
        return DatabaseConnectionError(
            "login_failed",
            "No se pudo iniciar sesión. Revisa el usuario y la contraseña.",
            401,
        )
    if "cannot open database" in message or "4060" in message:
        return DatabaseConnectionError(
            "database_not_found",
            "La base de datos no existe o no está accesible.",
            404,
        )
    if sqlstate in {"08001", "HYT00", "08004"} or any(
        token in message
        for token in (
            "timeout",
            "timed out",
            "server was not found",
            "network-related",
            "error locating server",
        )
    ):
        return DatabaseConnectionError(
            "server_unreachable",
            "No se pudo alcanzar SQL Server. Revisa el servidor, el puerto y que el servicio esté en ejecución.",
            503,
        )
    if sqlstate == "IM002" or (
        "data source name not found" in message or "driver" in message and "not found" in message
    ):
        return DatabaseConnectionError(
            "driver_not_found",
            "No se encontró el controlador ODBC. Instala ODBC Driver 18 for SQL Server.",
            500,
        )
    return DatabaseConnectionError(
        "connection_failed",
        "No se pudo conectar a SQL Server.",
        502,
    )


def _connect(params: ConnectionParams) -> pyodbc.Connection:
    try:
        return pyodbc.connect(
            build_connection_string(params),
            timeout=_CONNECT_TIMEOUT_SECONDS,
        )
    except pyodbc.Error as exc:
        raise translate_odbc_error(exc) from exc


def _query(connection: pyodbc.Connection, sql: str) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows: list[dict] = []
        for record in cursor.fetchall():
            rows.append(
                {
                    column: _json_value(value)
                    for column, value in zip(columns, record, strict=True)
                }
            )
        return rows


def _database_row(row: dict) -> dict:
    created = row.get("create_date")
    return {
        "name": row["name"],
        "database_id": row["database_id"],
        "state": row["state"],
        "recovery_model": row["recovery_model"],
        "create_date": created if isinstance(created, str) else None,
    }


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return value


def _validate(params: ConnectionParams) -> None:
    if not params.server.strip():
        raise DatabaseConnectionError(
            "invalid_connection",
            "Indica el nombre o la dirección del servidor.",
            422,
        )
    if params.port < 1 or params.port > 65535:
        raise DatabaseConnectionError(
            "invalid_connection",
            "El puerto debe estar entre 1 y 65535.",
            422,
        )
    if not params.database.strip():
        raise DatabaseConnectionError(
            "invalid_connection",
            "Indica la base de datos. Usa master para ver la instancia completa.",
            422,
        )
    if not params.driver.strip():
        raise DatabaseConnectionError(
            "invalid_connection",
            "Indica el controlador ODBC.",
            422,
        )
    if params.auth == "sql" and not params.username.strip():
        raise DatabaseConnectionError(
            "invalid_connection",
            "La autenticación de SQL Server requiere un usuario.",
            422,
        )
    for label, value in (
        ("servidor", params.server),
        ("base de datos", params.database),
        ("controlador", params.driver),
        ("usuario", params.username),
    ):
        if "\n" in value or "\r" in value:
            raise DatabaseConnectionError(
                "invalid_connection",
                f"El campo {label} contiene caracteres no válidos.",
                422,
            )


def _odbc_value(value: str) -> str:
    return "{" + value.replace("}", "}}") + "}"


def _public_error_text(exc: pyodbc.Error) -> str:
    text = " ".join(str(part) for part in exc.args)
    text = re.sub(r"(PWD=)\{.*?\}", r"\1***", text, flags=re.IGNORECASE)
    text = re.sub(r"(PWD=)[^;]*", r"\1***", text, flags=re.IGNORECASE)
    return text.lower()
