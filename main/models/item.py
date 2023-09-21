from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class ItemModel(BaseModel):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict | None] = mapped_column(nullable=True)
