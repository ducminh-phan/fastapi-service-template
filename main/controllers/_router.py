from fastapi import APIRouter

from . import probe

router = APIRouter()

router.include_router(probe.router, tags=["probe"])
