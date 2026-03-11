from fastapi import FastAPI
from loguru import logger
import sys

from api.auth import auth_router, router

logger.remove()
app_logger = logger.add(sys.stdout, level="INFO", colorize=True, enqueue=True)

app = FastAPI(title="PDF to audio")
app.include_router(auth_router)
app.include_router(router)