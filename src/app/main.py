import logging

from fastapi import FastAPI

from .routers import base, auth
from .config import get_config


def create_app() -> FastAPI:
    app = FastAPI()

    config = get_config()
    logging.basicConfig(level=config.LOG_LEVEL)

    app.include_router(base.router, prefix='')
    app.include_router(auth.router, prefix='/auth')

    return app


app = create_app()
