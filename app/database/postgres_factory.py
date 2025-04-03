from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


class SqlSessionManager:
    _engine = None
    _session_factory = None

    @classmethod
    def init_session(cls):
        if cls._engine is None:
            db_url = (
                f"postgresql+asyncpg://{settings.postgres_settings.db_user}:{settings.postgres_settings.db_password}"
                f"@{settings.postgres_settings.db_host}/{settings.postgres_settings.db_name}"
            )
            cls._engine = create_async_engine(db_url, echo=True)
            cls._session_factory = async_sessionmaker(
                bind=cls._engine, class_=AsyncSession, expire_on_commit=False
            )

    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncSession:
        if cls._session_factory is None:
            raise RuntimeError("DatabaseSessionManager не был инициализирован.")

        async with cls._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @classmethod
    async def close(cls):
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
