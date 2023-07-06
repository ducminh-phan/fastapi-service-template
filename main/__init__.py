from importlib import import_module

from ._app import app
from ._config import config
from ._db import db
from .commons.error_handlers import register_error_handlers


def register_subpackages():
    from main import models
    from main.controllers import router

    for m in models.__all__:
        import_module(f"main.models.{m}")

    app.include_router(router)


register_subpackages()
register_error_handlers(app)
