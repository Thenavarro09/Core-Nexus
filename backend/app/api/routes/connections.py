from fastapi import APIRouter

from app.core.config import get_settings
from app.db.connection import ConnectionParams, inspect_server, list_databases, params_from_settings
from app.schemas.connections import (
    ConnectionTestRequest,
    ConnectionTestResponse,
    DatabaseListResponse,
)

router = APIRouter(tags=["connections"])


@router.post("/api/connections/test", response_model=ConnectionTestResponse)
def test_connection(body: ConnectionTestRequest) -> ConnectionTestResponse:
    params = ConnectionParams(
        server=body.server.strip(),
        port=body.port,
        database=body.database.strip() or "master",
        auth=body.auth,
        username=body.username,
        password=body.password,
        driver=body.driver.strip() or "ODBC Driver 18 for SQL Server",
        trust_server_certificate=body.trust_server_certificate,
    )
    return ConnectionTestResponse.model_validate(inspect_server(params))


@router.get("/api/databases", response_model=DatabaseListResponse)
def get_databases() -> DatabaseListResponse:
    params = params_from_settings(get_settings())
    return DatabaseListResponse(databases=list_databases(params))
