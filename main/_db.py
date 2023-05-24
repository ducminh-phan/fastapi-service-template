import secrets
from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from ._config import config


class Database:
    """
    Set up and contain our database connections.

    This is used to be able to set up the database in a uniform way
    while allowing easy testing and session management.

    Session management is done using ``scoped_session`` with a special scope func,
    because we cannot use threading.local(). ContextVar does the right thing with
    respect to asyncio and behaves similar to threading.local().

    We only store a random string in the context var and let scoped session do
    the heavy lifting. This allows us to easily start a new session or get the
    existing one using the async_scoped_session mechanism.
    """

    def __init__(self):
        self.request_id_context: ContextVar[str] = ContextVar(
            "request_id_context",
            default="",
        )

        self.engine = create_async_engine(
            config.SQLALCHEMY_DATABASE_URI,
            echo=config.SQLALCHEMY_ECHO,
            pool_pre_ping=True,
            **config.SQLALCHEMY_ENGINE_OPTIONS,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

        self.scoped_session = async_scoped_session(
            self.session_factory,
            self._scope_func,
        )

    def _scope_func(self) -> str:
        request_id = self.request_id_context.get()
        return request_id

    @property
    def session(self) -> AsyncSession:
        return self.scoped_session()

    @asynccontextmanager
    async def scope(self):
        """
        Create a new database session (scope).

        This creates a new database session to handle all the database connection
        from a single scope (request). This method should typically only been called
        in request middleware.
        """

        token = self.request_id_context.set(secrets.token_hex())
        self.scoped_session()

        yield

        await self.scoped_session.remove()
        self.request_id_context.reset(token)


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        async with db.scope():
            response = await call_next(request)

        return response


db = Database()
