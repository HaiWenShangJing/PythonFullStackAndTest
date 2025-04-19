import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.db import get_session
from backend.app.main import app
from backend.app.models import Base

# 从环境变量获取测试数据库配置
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "db")  # 在Docker环境中使用服务名称
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "ai_crud_test")

# 构建测试数据库URL
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"Using test database: {TEST_DATABASE_URL}")

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False,
    poolclass=NullPool,
)

# Create test session
test_async_session = sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Override the get_session dependency
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Apply the override
app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Set up the test database"""
    print("Setting up test database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    print("Tearing down test database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session"""
    async with test_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Get a test client for FastAPI"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client