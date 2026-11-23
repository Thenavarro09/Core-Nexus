from fastapi import APIRouter

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("")
def monitoring_status() -> dict[str, str]:
    return {"module": "monitoring", "status": "pending"}
