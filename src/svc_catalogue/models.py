"""Database models for the Service Catalogue."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class Service(SQLModel, table=True):
    """Service domain model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(index=True, unique=True, min_length=1, max_length=255)
    owner_team: str = Field(index=True, min_length=1, max_length=255)
    tier: str = Field(index=True)
    lifecycle: str = Field(index=True)
    endpoints: List[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    tags: List[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
