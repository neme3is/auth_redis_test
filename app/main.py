from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config import settings
from app.logger import Logger
from app.routes.auth import router as auth_router
from app.routes.protected_sources import router as protected_router
from app.routes.registration import router as registration_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Logger.get_logger()
    Logger.logger.info("Logger initialized")
    # SqlSessionManager.init_session()
    # Logger.logger.info("✅ Database initialized")

    yield

    # await SqlSessionManager.close()
    # Logger.logger.info("❌ Database connection closed")


app = FastAPI(lifespan=lifespan)
app.include_router(registration_router)
app.include_router(auth_router)
app.include_router(protected_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app_settings.app_host, port=settings.app_settings.app_port, reload=True)
