from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from contextlib import asynccontextmanager
from app.config import settings


DATABASE_URL = (f"postgresql+asyncpg://{settings.postgres_settings.db_user}:{settings.postgres_settings.db_password}"
                f"@{settings.postgres_settings.db_host}/{settings.postgres_settings.db_name}")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
