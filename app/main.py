from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.database.postgres_factory import SqlSessionManager
from app.routes.auth import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SqlSessionManager.init_session()
    print("✅ Database initialized")

    yield  # Переход к работе сервиса

    await SqlSessionManager.close()
    print("❌ Database connection closed")


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
