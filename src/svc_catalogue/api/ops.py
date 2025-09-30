"""Operational endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from .dependencies import DBSession

router = APIRouter(tags=["ops"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@router.get("/ready")
def readiness(session: DBSession) -> dict[str, str]:
    """Readiness probe verifying database connectivity."""
    session.exec(text("SELECT 1"))
    return {"status": "ready"}
