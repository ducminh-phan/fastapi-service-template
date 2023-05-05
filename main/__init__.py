from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ._config import config
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
