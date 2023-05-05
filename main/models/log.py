"""
This file is an example for the sake of completeness, meant to be removed.
"""

from sqlalchemy import JSON, Column, Integer

from .base import BaseModel


class LogModel(BaseModel):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=True)
