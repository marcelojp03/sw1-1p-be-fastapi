from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.auth_middleware import InternalKeyMiddleware
from app.routers import analyze_bottlenecks, suggest_form_fields, suggest_workflow

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — solo red interna / Spring Boot
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Internal key authentication
app.add_middleware(InternalKeyMiddleware)

# Routers
app.include_router(suggest_workflow.router, prefix="/api/ai")
app.include_router(suggest_form_fields.router, prefix="/api/ai")
app.include_router(analyze_bottlenecks.router, prefix="/api/ai")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME}
