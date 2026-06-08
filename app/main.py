from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.auth_middleware import InternalKeyMiddleware
from app.routers import (
    analyze_bottlenecks,
    convert_document,
    fill_form,
    generate_diagram,
    identify_policy,
    nl_report,
    routing_predict,
    suggest_form_fields,
    suggest_workflow,
    transcribe_audio,
)

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

# Routers — Ciclo 1
app.include_router(suggest_workflow.router, prefix="/api/ai")
app.include_router(suggest_form_fields.router, prefix="/api/ai")
app.include_router(analyze_bottlenecks.router, prefix="/api/ai")
app.include_router(generate_diagram.router, prefix="/api/ai")

# Routers — Ciclo 2
app.include_router(convert_document.router, prefix="/api/ai")
app.include_router(transcribe_audio.router, prefix="/api/ai")
app.include_router(identify_policy.router, prefix="/api/ai")
app.include_router(fill_form.router, prefix="/api/ai")
app.include_router(nl_report.router, prefix="/api/ai")
app.include_router(routing_predict.router, prefix="/api/ai")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME}
