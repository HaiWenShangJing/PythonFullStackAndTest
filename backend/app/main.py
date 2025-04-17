import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db import create_db_and_tables, get_engine
from backend.app.routers import ai, items

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# 使用绝对路径加载.env文件
print(f"Loading .env from: {ENV_FILE}")
load_dotenv(dotenv_path=ENV_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist
    await create_db_and_tables()
    
    yield
    
    # Shutdown: close engine
    engine = get_engine()
    await engine.dispose()


app = FastAPI(
    title="Full-Stack AI CRUD API",
    description="API for a full-stack application with CRUD operations and AI chat",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Full-Stack AI CRUD API"}


@app.get("/api/v1/")
async def api_root():
    """API根路径，用于健康检查"""
    return {"status": "ok", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)