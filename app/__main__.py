from fastapi import FastAPI

from app.config import config
from app.handlers.general.lifespan import lifespan
from app.setup import (
    setup_logging,
    setup_handlers,
    setup_middlewares,
    setup_dependencies,
)

fastapi_app = FastAPI(
    debug=config.is_dev_mode,
    lifespan=lifespan,
    root_path="/api/v1",
    version="1.0.0",
    redoc_url="/docs" if config.is_dev_mode else None,
    docs_url="/swagger_docs" if config.is_dev_mode else None,
)

setup_logging()
setup_dependencies(fastapi_app)
setup_handlers(fastapi_app)
setup_middlewares(fastapi_app)
