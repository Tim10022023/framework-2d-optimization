import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.session import Base, engine
from app.db import models
from app.api.functions import router as functions_router
from app.api.sessions import router as sessions_router
from app.core.config import settings
from app.core.redis import init_redis, close_redis
from app.core.websocket import manager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Startup: Initialize Redis
    await init_redis()

    # Startup: Run Redis Pub/Sub listener in the background
    pubsub_task = asyncio.create_task(manager.pubsub_listener())
    
    yield
    # Shutdown: Clean up
    pubsub_task.cancel()
    await engine.dispose()
    await close_redis()

app = FastAPI(title="2D Optimization Framework", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

cors_origins_env = os.getenv(
    "BACKEND_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
)
allow_origins = [
    origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(functions_router)
app.include_router(sessions_router)
