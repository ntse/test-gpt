"""Service routes."""
from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlmodel import Session

from ...crud import (
    ServiceAlreadyExistsError,
    ServiceNotFoundError,
    create_service,
    delete_service,
    get_service,
    list_services,
    update_service,
)
from ...csv_import import CSVImportException, import_services_from_csv, load_csv_content
from ...schemas import CSVImportResult, ServiceCreate, ServiceList, ServiceRead, ServiceUpdate
from ..dependencies import DBSession, require_token

router = APIRouter(prefix="/services", tags=["services"])

TokenDep = Annotated[None, Depends(require_token)]


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service_endpoint(
    service_in: ServiceCreate,
    _: TokenDep,
    session: DBSession,
) -> ServiceRead:
    try:
        service = create_service(session, service_in)
    except ServiceAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ServiceRead.model_validate(service, from_attributes=True)


@router.post("/import", response_model=CSVImportResult, status_code=status.HTTP_202_ACCEPTED)
def import_services(
    _: TokenDep,
    session: DBSession,
    file: UploadFile = File(..., description="CSV file with service data"),
) -> CSVImportResult:
    try:
        buffer = load_csv_content(file)
        result = import_services_from_csv(session, buffer)
    except CSVImportException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        file.file.close()
    return result


@router.get("", response_model=ServiceList)
def list_services_endpoint(
    _: TokenDep,
    session: DBSession,
    owner_team: Optional[str] = Query(default=None),
    tier: Optional[str] = Query(default=None),
    lifecycle: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ServiceList:
    services, total = list_services(
        session,
        owner_team=owner_team,
        tier=tier,
        lifecycle=lifecycle,
        search=search,
        limit=limit,
        offset=offset,
    )
    items = [ServiceRead.model_validate(service, from_attributes=True) for service in services]
    return ServiceList(items=items, total=total)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service_endpoint(
    service_id: UUID,
    _: TokenDep,
    session: DBSession,
) -> ServiceRead:
    try:
        service = get_service(session, service_id)
    except ServiceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ServiceRead.model_validate(service, from_attributes=True)


@router.put("/{service_id}", response_model=ServiceRead)
def update_service_endpoint(
    service_id: UUID,
    service_in: ServiceUpdate,
    _: TokenDep,
    session: DBSession,
) -> ServiceRead:
    try:
        service = get_service(session, service_id)
    except ServiceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    service = update_service(session, service, service_in)
    return ServiceRead.model_validate(service, from_attributes=True)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_endpoint(
    service_id: UUID,
    _: TokenDep,
    session: DBSession,
) -> Response:
    try:
        service = get_service(session, service_id)
    except ServiceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    delete_service(session, service)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
