from sqlalchemy import func, select

from main import db
from main.models.item import ItemModel


async def count_items() -> int:
    statement = select(func.count()).select_from(ItemModel)
    result = await db.session.execute(statement)
    return result.scalar()


async def add_item() -> ItemModel:
    item = ItemModel(data={})

    db.session.add(item)
    await db.session.commit()

    return item
