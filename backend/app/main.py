import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db import create_db_and_tables, get_engine
from backend.app.routers import ai, items

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


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)