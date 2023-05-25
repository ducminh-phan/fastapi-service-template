from fastapi import APIRouter

from main.engines.items import add_item, count_items

router: APIRouter = APIRouter()


@router.get("/items/count")
async def get_items_count():
    count = await count_items()

    return {
        "count": count,
    }


@router.post("/items")
async def _add_item():
    await add_item()

    return {}
