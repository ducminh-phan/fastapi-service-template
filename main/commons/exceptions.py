from fastapi.responses import JSONResponse

from main.schemas.exceptions import ErrorSchema


class StatusCode:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500


class ErrorCode:
    BAD_REQUEST = 400000
    VALIDATION_ERROR = 400001
    UNAUTHORIZED = 401000
    FORBIDDEN = 403000
    NOT_FOUND = 404000
    METHOD_NOT_ALLOWED = 405000
    INTERNAL_SERVER_ERROR = 500000


class _ErrorMessage:
    BAD_REQUEST = "Bad request."
    VALIDATION_ERROR = "Validation error."
    UNAUTHORIZED = "Unauthorized."
    FORBIDDEN = "Forbidden."
    NOT_FOUND = "Not found."
    METHOD_NOT_ALLOWED = "Method not allowed."
    INTERNAL_SERVER_ERROR = "Internal server error."


class BaseError(Exception):
    def __init__(
        self,
        *,
        error_message=None,
        error_data=None,
        status_code: int | None = None,
        error_code: int | None = None,
    ):
        """
        Customize the response exception

        :param error_message: <string> Message field in the response body
        :param status_code: <number> HTTP status code
        :param error_data: <dict> Json body data
        :param error_code: <number> error code
        """
        if error_message is not None:
            self.error_message = error_message

        if status_code is not None:
            self.status_code = status_code

        if error_code is not None:
            self.error_code = error_code

        self.error_data = error_data

    def to_response(self):
        return JSONResponse(
            ErrorSchema.model_validate(self).model_dump(mode="json"),
            self.status_code,
        )


class BadRequest(BaseError):
    status_code = StatusCode.BAD_REQUEST
    error_message = _ErrorMessage.BAD_REQUEST
    error_code = ErrorCode.BAD_REQUEST


class ValidationError(BaseError):
    status_code = StatusCode.BAD_REQUEST
    error_message = _ErrorMessage.VALIDATION_ERROR
    error_code = ErrorCode.VALIDATION_ERROR


class Unauthorized(BaseError):
    status_code = StatusCode.UNAUTHORIZED
    error_message = _ErrorMessage.UNAUTHORIZED
    error_code = ErrorCode.UNAUTHORIZED


class Forbidden(BaseError):
    status_code = StatusCode.FORBIDDEN
    error_message = _ErrorMessage.FORBIDDEN
    error_code = ErrorCode.FORBIDDEN


class NotFound(BaseError):
    status_code = StatusCode.NOT_FOUND
    error_message = _ErrorMessage.NOT_FOUND
    error_code = ErrorCode.NOT_FOUND


class InternalServerError(BaseError):
    status_code = StatusCode.INTERNAL_SERVER_ERROR
    error_message = _ErrorMessage.INTERNAL_SERVER_ERROR
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
