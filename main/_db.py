import secrets
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from typing import ParamSpec, TypeVar

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from ._config import config

T = TypeVar("T")
P = ParamSpec("P")


def generate_request_id() -> str:
    return secrets.token_hex()


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
        return self.request_id_context.get()

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

        token = self.request_id_context.set(generate_request_id())
        self.scoped_session()

        try:
            yield

        finally:
            await self.scoped_session.remove()
            self.request_id_context.reset(token)

    def with_scope(self, f: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(f)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            async with self.scope():
                return await f(*args, **kwargs)

        return wrapper


db = Database()
