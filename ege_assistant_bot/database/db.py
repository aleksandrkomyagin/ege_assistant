from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_pool(
        dsn: str | URL
) -> async_sessionmaker[AsyncSession]:
    engine: AsyncEngine = create_async_engine(url=dsn)
    return async_sessionmaker(engine, expire_on_commit=False)
