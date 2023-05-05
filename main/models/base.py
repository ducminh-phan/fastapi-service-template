from datetime import datetime
from typing import Type

from sqlalchemy import Column, DateTime, MetaData
from sqlalchemy.orm import DeclarativeMeta, declarative_base

BaseModel: Type[DeclarativeMeta] = declarative_base(
    metadata=MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "ix": "ix_%(column_0_N_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(column_0_N_name)s",
        }
    )
)


class TimestampMixin:
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
