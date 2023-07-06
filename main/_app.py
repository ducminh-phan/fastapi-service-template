from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ._config import config
from .middlewares import (
    AccessLogMiddleware,
    DBSessionMiddleware,
)

api_docs_enabled = config.ENVIRONMENT == "local"

app = FastAPI(
    redoc_url=None,
    docs_url="/docs" if api_docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware)
app.add_middleware(AccessLogMiddleware)
