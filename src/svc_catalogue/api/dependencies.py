"""Common API dependencies."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from ..config import settings
from ..db import get_session


def _db_session() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


DBSession = Annotated[Session, Depends(_db_session)]


_bearer_scheme = HTTPBearer(auto_error=False)


def require_token(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Security(_bearer_scheme)
    ],
) -> None:
    """Simple bearer token validation."""
    if credentials is None or credentials.credentials != settings.auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
