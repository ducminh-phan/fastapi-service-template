from typing import Any

from .base import BaseResponseSchema


class ErrorSchema(BaseResponseSchema):
    error_message: str | None = None
    error_data: Any | None = None
    error_code: int | None = None
