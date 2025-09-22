"""Pydantic schemas for the Service Catalogue."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, constr, field_validator
from pydantic.config import ConfigDict


class ServiceTier(str, Enum):
    gold = "gold"
    silver = "silver"
    bronze = "bronze"


class ServiceLifecycle(str, Enum):
    production = "production"
    preprod = "preprod"
    dev = "dev"
    deprecated = "deprecated"


class ServiceBase(BaseModel):
    name: constr(min_length=1, max_length=255)
    owner_team: constr(min_length=1, max_length=255)
    tier: ServiceTier
    lifecycle: ServiceLifecycle
    endpoints: List[HttpUrl] = Field(default_factory=list)
    tags: List[constr(min_length=1, max_length=50)] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    def lower_tag(cls, value: Optional[List[str]]) -> List[str]:  # noqa: N805
        if not value:
            return []
        return [item.strip().lower() for item in value]


class ServiceCreate(ServiceBase):
    id: Optional[UUID] = Field(default_factory=uuid4)


class ServiceUpdate(BaseModel):
    owner_team: Optional[constr(min_length=1, max_length=255)] = None
    tier: Optional[ServiceTier] = None
    lifecycle: Optional[ServiceLifecycle] = None
    endpoints: Optional[List[HttpUrl]] = None
    tags: Optional[List[constr(min_length=1, max_length=50)]] = None

    @field_validator("tags", mode="before")
    def lower_tag(cls, value: Optional[List[str]]) -> Optional[List[str]]:  # noqa: N805
        if value is None:
            return value
        return [item.strip().lower() for item in value]


class ServiceRead(ServiceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceList(BaseModel):
    items: List[ServiceRead]
    total: int


class CSVImportResult(BaseModel):
    created: int
    updated: int
    errors: List[str] = Field(default_factory=list)
    total_rows: int
