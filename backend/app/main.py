from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import administration, connections, health, monitoring
from app.core.exceptions import DatabaseConnectionError

app = FastAPI(
    title="Core-Nexus",
    summary="Suite de administración y monitoreo de SQL Server.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(
    _request: Request,
    exc: DatabaseConnectionError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


app.include_router(health.router)
app.include_router(connections.router)
app.include_router(monitoring.router)
app.include_router(administration.router)
