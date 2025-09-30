"""FastAPI application entrypoint."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .api import ops
from .api.v1 import services
from .config import settings
from .db import init_db

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ops.router)
app.include_router(services.router, prefix="/api/v1")

Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", tags=["meta"])
def read_root() -> dict[str, Any]:
    """Simple index endpoint."""
    return {"message": "Service Catalogue API"}
