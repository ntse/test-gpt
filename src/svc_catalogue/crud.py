"""CRUD operations for services."""

from __future__ import annotations

from typing import Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from .models import Service
from .schemas import ServiceCreate, ServiceUpdate


class ServiceAlreadyExistsError(RuntimeError):
    """Raised when a service with the same name already exists."""


class ServiceNotFoundError(RuntimeError):
    """Raised when a service cannot be found."""


def create_service(session: Session, service_in: ServiceCreate) -> Service:
    """Create a new service entry."""
    payload = service_in.model_dump(mode="json")
    service = Service(**payload)
    session.add(service)
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        raise ServiceAlreadyExistsError(
            "Service with this name already exists"
        ) from exc
    session.refresh(service)
    return service


def get_service(session: Session, service_id: UUID) -> Service:
    """Fetch a service by id."""
    service = session.get(Service, str(service_id))
    if not service:
        raise ServiceNotFoundError("Service not found")
    return service


def get_service_by_name(session: Session, name: str) -> Optional[Service]:
    """Fetch a service by name."""
    statement = select(Service).where(func.lower(Service.name) == name.lower())
    return session.exec(statement).scalar_one_or_none()


def list_services(
    session: Session,
    *,
    owner_team: Optional[str] = None,
    tier: Optional[str] = None,
    lifecycle: Optional[str] = None,
    search: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
) -> Tuple[Sequence[Service], int]:
    """List services with optional filters."""
    statement = select(Service)

    if owner_team:
        statement = statement.where(
            func.lower(Service.owner_team) == owner_team.lower()
        )
    if tier:
        statement = statement.where(Service.tier == tier)
    if lifecycle:
        statement = statement.where(Service.lifecycle == lifecycle)
    if search:
        like_pattern = f"%{search.lower()}%"
        tags_text = cast(Service.tags, String)
        statement = statement.where(
            or_(
                func.lower(Service.name).like(like_pattern),
                func.lower(tags_text).like(like_pattern),
            )
        )

    count_stmt = statement.with_only_columns(func.count()).order_by(None)
    total_row = session.exec(count_stmt).one()
    if isinstance(total_row, tuple):
        total = total_row[0]
    elif hasattr(total_row, "__getitem__"):
        total = total_row[0]
    else:
        total = total_row
    statement = statement.offset(offset).limit(limit)
    raw_results = session.exec(statement).all()
    services = [row if isinstance(row, Service) else row[0] for row in raw_results]
    return services, total


def update_service(
    session: Session, service: Service, service_in: ServiceUpdate
) -> Service:
    """Update a service with partial changes."""
    data = service_in.model_dump(exclude_unset=True, mode="json")
    for key, value in data.items():
        setattr(service, key, value)
    session.add(service)
    session.flush()
    session.refresh(service)
    return service


def delete_service(session: Session, service: Service) -> None:
    """Delete a service."""
    session.delete(service)
    session.flush()
