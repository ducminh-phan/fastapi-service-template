from sqlalchemy import func, select

from main import db
from main.models.log import LogModel


async def test_log():
    async def count_logs() -> int:
        statement = select(func.count()).select_from(LogModel)
        result = await db.session.execute(statement)
        return result.scalar()

    assert (await count_logs()) == 0

    db.session.add(LogModel(data={}))
    await db.session.commit()

    await db.session.scalars(statement=select(LogModel))

    assert (await count_logs()) == 1
