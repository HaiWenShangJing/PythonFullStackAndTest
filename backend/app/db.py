import os
from typing import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.models import Base

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# 使用绝对路径加载.env文件
load_dotenv(dotenv_path=ENV_FILE)

# Get database URL from environment variable with a fallback for development
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_crud"
)

# Create engine with connection pooling for production, NullPool for testing
pooling = os.environ.get("ENVIRONMENT") != "test"
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    future=True,
    poolclass=None if pooling else NullPool,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False, autocommit=False
)


async def create_db_and_tables():
    """Create database tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_engine():
    """Return the current engine"""
    return engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise