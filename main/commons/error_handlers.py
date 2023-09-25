from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from main.libs.log import get_logger

from .exceptions import BaseError, InternalServerError, StatusCode, ValidationError

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_, exc: StarletteHTTPException):
        return BaseError(
            error_message=exc.detail,
            error_code=exc.status_code * 1000,
            status_code=exc.status_code,
        ).to_response()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_, exc: RequestValidationError):
        return ValidationError(
            error_data=jsonable_encoder(
                exc.errors(),
                custom_encoder={
                    Exception: str,
                },
            ),
        ).to_response()

    @app.exception_handler(BaseError)
    async def handle_error(_, error: BaseError):
        status_code = error.status_code
        if (
            isinstance(status_code, int)
            and status_code != StatusCode.INTERNAL_SERVER_ERROR
        ):
            logging_method = logger.warning
        else:
            logging_method = logger.error

        logging_method(
            error.error_message,
            data={
                "error_data": error.error_data,
                "error_code": error.error_code,
            },
        )
        return error.to_response()

    @app.exception_handler(Exception)
    async def handle_exception(_, e):
        logger.exception(str(e))

        return InternalServerError().to_response()
