from sqlalchemy import JSON, Column, Integer

from .base import BaseModel


class ItemModel(BaseModel):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=True)
