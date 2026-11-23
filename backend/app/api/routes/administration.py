from fastapi import APIRouter

router = APIRouter(prefix="/api/administration", tags=["administration"])


@router.get("")
def administration_status() -> dict[str, str]:
    return {"module": "administration", "status": "pending"}
