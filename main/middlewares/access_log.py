"""
The code in this module was copied from
https://github.com/Kludex/asgi-logger/blob/main/asgi_logger/middleware.py
with some modifications
"""

import http
import logging
import os
import sys
import time
from typing import TYPE_CHECKING, TypedDict

from uvicorn.protocols.utils import get_client_addr, get_path_with_query_string

if TYPE_CHECKING:
    from asgiref.typing import (
        ASGI3Application,
        ASGIReceiveCallable,
        ASGISendCallable,
        ASGISendEvent,
        HTTPScope,
    )


class AccessInfo(TypedDict, total=False):
    response: "ASGISendEvent"
    start_time: float
    end_time: float


class AccessLogMiddleware:
    # 127.0.0.6 - - [2023-06-16 05:20:48,983] "GET /ready HTTP/1.1"
    # 200 2 "-" "kube-probe/1.22+" "1.2.3.4" 0.002
    DEFAULT_FORMAT = (
        '%(h)s %(l)s %(u)s %(t)s "%(R)s" '
        '%(s)d %(B)s "%(f)s" "%(a)s" "%(x_forwarded_for)s" %(L).3f'
    )

    def __init__(
        self,
        app: "ASGI3Application",
        log_format: str | None = None,
        logger: logging.Logger | None = None,
    ):
        self.app = app
        self.format = log_format or self.DEFAULT_FORMAT

        if logger is None:
            self.logger = logging.getLogger("http.access")
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)
        else:
            self.logger = logger

        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.disabled = True

    async def __call__(
        self,
        scope: "HTTPScope",
        receive: "ASGIReceiveCallable",
        send: "ASGISendCallable",
    ):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)  # pragma: no cover

        info = AccessInfo(response={})

        async def wrapped_send(message: "ASGISendEvent"):
            if message["type"] == "http.response.start":
                info["response"] = message
                info["end_time"] = time.time()
                self.log(scope, info)

            await send(message)

        info["start_time"] = time.time()
        await self.app(scope, receive, wrapped_send)

    def log(self, scope: "HTTPScope", info: AccessInfo):
        self.logger.info(self.format, AccessLogAtoms(scope, info))


class AccessLogAtoms(dict):
    def __init__(self, scope: "HTTPScope", info: AccessInfo):
        super().__init__()

        for name, value in scope["headers"]:
            self[f"{{{name.decode('latin1').lower()}}}i"] = value.decode("latin1")
        for name, value in info["response"].get("headers", []):
            self[f"{{{name.decode('latin1').lower()}}}o"] = value.decode("latin1")
        for name, value in os.environ.items():
            self[f"{{{name.lower()!r}}}e"] = value

        protocol = f"HTTP/{scope['http_version']}"

        status = info["response"]["status"]
        try:
            status_phrase = http.HTTPStatus(status).phrase
        except ValueError:
            status_phrase = "-"

        path = scope["root_path"] + scope["path"]
        full_path = get_path_with_query_string(scope)
        request_line = f"{scope['method']} {path} {protocol}"
        full_request_line = f"{scope['method']} {full_path} {protocol}"

        request_time = info["end_time"] - info["start_time"]
        client_host = scope["client"][0]
        client_addr = get_client_addr(scope)
        self.update(
            {
                "h": client_host,
                "client_addr": client_addr,
                "l": "-",
                "u": "-",  # Not available on ASGI.
                "t": time.strftime("[%d/%b/%Y:%H:%M:%S %z]"),
                "r": request_line,
                "request_line": full_request_line,
                "R": full_request_line,
                "m": scope["method"],
                "U": scope["path"],
                "q": scope["query_string"].decode(),
                "H": protocol,
                "s": status,
                "status_code": f"{status} {status_phrase}",
                "st": status_phrase,
                "B": self["{Content-Length}o"],
                "b": self.get("{Content-Length}o", "-"),
                "f": self["{Referer}i"],
                "a": self["{User-Agent}i"],
                "T": int(request_time),
                "M": int(request_time * 1_000),
                "D": int(request_time * 1_000_000),
                "L": request_time,
                "p": f"<{os.getpid()}>",
                "x_forwarded_for": get_x_forwarded_for(scope) or "-",
            },
        )

    def __getitem__(self, key: str) -> str:
        try:
            if key.startswith("{"):
                return super().__getitem__(key.lower())
            else:
                return super().__getitem__(key)
        except KeyError:
            return "-"


def get_x_forwarded_for(scope: "HTTPScope") -> str | None:
    headers = dict(scope["headers"])
    if b"x-forwarded-for" not in headers:
        return None

    x_forwarded_for = headers[b"x-forwarded-for"].decode("latin1")
    x_forwarded_for_hosts = [item.strip() for item in x_forwarded_for.split(",")]

    return x_forwarded_for_hosts[-1] if x_forwarded_for_hosts else None
