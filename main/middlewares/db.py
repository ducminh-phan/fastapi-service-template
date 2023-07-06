from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asgiref.typing import (
        ASGI3Application,
        ASGIReceiveCallable,
        ASGISendCallable,
        HTTPScope,
    )


class DBSessionMiddleware:
    def __init__(self, app: "ASGI3Application"):
        self.app = app

    async def __call__(
        self,
        scope: "HTTPScope",
        receive: "ASGIReceiveCallable",
        send: "ASGISendCallable",
    ):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)  # pragma: no cover

        from main import db

        async with db.scope():
            await self.app(scope, receive, send)
