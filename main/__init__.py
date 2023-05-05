from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ._config import config
from ._db import DBSessionMiddleware, db
from .commons.error_handlers import register_error_handlers
from .controllers import router

app = FastAPI(
    redoc_url=None,
    docs_url=None if config.ENVIRONMENT == "production" else "/docs",
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware, db=db)

register_error_handlers(app)