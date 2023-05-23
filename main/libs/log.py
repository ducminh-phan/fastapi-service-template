import json
import logging
import sys
import time
from functools import cached_property

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from main import config


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(config.LOGGING_LEVEL)

    formatter = logging.Formatter(
        "[%(asctime)s][%(name)s][%(levelname)s]"
        " (%(module)s:%(funcName)s:%(lineno)d) %(message)s"
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    logger.propagate = False

    return logger


class _CustomLogger(logging.Logger):
    def _log(  # type: ignore[override]
        self,
        level: int,
        msg: str,
        args,
        data=None,
        **kwargs,
    ):
        if data:
            msg = f"{msg} | {json.dumps(data, default=str)}"

        # noinspection PyProtectedMember
        super()._log(level, msg, args, **kwargs)


logging.Logger.manager.loggerClass = _CustomLogger


class AccessLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.disabled = True

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        from uvicorn.protocols.utils import get_path_with_query_string

        start_time = time.monotonic()

        response = await call_next(request)

        end_time = time.monotonic()
        request_time = end_time - start_time

        method = request.scope["method"]
        path = get_path_with_query_string(request.scope)
        http_version = request.scope["http_version"]
        request_line = f"{method} {path} HTTP/{http_version}"

        self.__logger.info(
            request_line,
            extra={
                "remote_addr": request.client.host,
                "status_code": response.status_code,
                "content_length": response.headers.get("content-length", "-"),
                "referer": request.headers.get("referer", "-"),
                "user_agent": request.headers.get("user-agent", "-"),
                "x_forwarded_for": request.headers.get("x-forwarded-for", "-"),
                "request_time": request_time,
            },
        )

        return response

    @cached_property
    def __logger(self):
        logger = logging.getLogger("http.access")
        logger.setLevel(config.LOGGING_LEVEL)

        formatter = logging.Formatter(
            '%(remote_addr)s - - [%(asctime)s] "%(message)s" '
            "%(status_code)s %(content_length)s "
            '"%(referer)s" "%(user_agent)s" "%(x_forwarded_for)s" '
            "%(request_time).3f"
        )

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False

        return logger
