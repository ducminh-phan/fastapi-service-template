from fastapi import APIRouter

from . import items, probe

router = APIRouter()

router.include_router(probe.router, tags=["probe"])
router.include_router(items.router, tags=["items"])
