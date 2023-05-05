from fastapi import APIRouter

router = APIRouter()


@router.get("/pings")
async def ping():
    return {}


@router.get("/ready")
async def is_ready():
    return {}
