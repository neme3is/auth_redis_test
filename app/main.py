from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.database.postgres_factory import SqlSessionManager
from app.logger import Logger
from app.routes.auth import router as auth_router
from app.routes.registration import router as registration_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Logger.get_logger()
    Logger.logger.info('Logger initialized')
    #SqlSessionManager.init_session()
    #Logger.logger.info("✅ Database initialized")

    yield

    #await SqlSessionManager.close()
    Logger.logger.info("❌ Database connection closed")


app = FastAPI(lifespan=lifespan)
app.include_router(registration_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
