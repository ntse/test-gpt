"""CSV import utilities for services."""

from __future__ import annotations

import csv
from io import StringIO, TextIOBase
from typing import Optional
from uuid import UUID

from fastapi import UploadFile
from pydantic import ValidationError
from sqlmodel import Session

from .config import settings
from .crud import create_service, get_service_by_name, update_service
from .schemas import CSVImportResult, ServiceCreate, ServiceUpdate

EXPECTED_HEADERS = {
    "name",
    "owner_team",
    "tier",
    "lifecycle",
    "endpoints",
    "tags",
    "id",
}


class CSVImportException(Exception):
    """Raised when the CSV import cannot proceed."""


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def _coerce_uuid(value: Optional[str]) -> Optional[UUID]:
    if not value:
        return None
    return UUID(value)


def load_csv_content(upload: UploadFile) -> StringIO:
    """Read upload content as UTF-8 string buffer."""
    content = upload.file.read()
    if isinstance(content, bytes):
        text = content.decode("utf-8")
    else:
        text = content
    return StringIO(text)


def import_services_from_csv(session: Session, file_obj: TextIOBase) -> CSVImportResult:
    """Create or update services from a CSV file."""
    reader = csv.DictReader(file_obj)
    if reader.fieldnames is None:
        raise CSVImportException("CSV missing header row")

    unknown = set(reader.fieldnames) - EXPECTED_HEADERS
    missing = EXPECTED_HEADERS - set(reader.fieldnames)
    if unknown:
        raise CSVImportException(f"Unknown columns: {', '.join(sorted(unknown))}")
    if missing - {"id"}:
        raise CSVImportException(
            f"Missing required columns: {', '.join(sorted(missing - {'id'}))}"
        )

    created = 0
    updated = 0
    errors: list[str] = []
    total_rows = 0

    for row in reader:
        total_rows += 1
        if total_rows > settings.csv_max_rows:
            errors.append(
                f"row {total_rows}: exceeded maximum allowed rows ({settings.csv_max_rows})"
            )
            break
        try:
            endpoints = _parse_list(row.get("endpoints", ""))
            tags = _parse_list(row.get("tags", ""))
            payload = ServiceCreate(
                id=_coerce_uuid(row.get("id")) or None,
                name=row.get("name", ""),
                owner_team=row.get("owner_team", ""),
                tier=row.get("tier") or "",
                lifecycle=row.get("lifecycle") or "",
                endpoints=endpoints,
                tags=tags,
            )
        except (ValueError, ValidationError) as exc:
            errors.append(f"row {total_rows}: {exc}")
            continue

        existing = get_service_by_name(session, payload.name)
        if existing:
            update_data = ServiceUpdate(
                owner_team=payload.owner_team,
                tier=payload.tier,
                lifecycle=payload.lifecycle,
                endpoints=payload.endpoints,
                tags=payload.tags,
            )
            update_service(session, existing, update_data)
            updated += 1
        else:
            create_service(session, payload)
            created += 1

    return CSVImportResult(
        created=created,
        updated=updated,
        errors=errors,
        total_rows=total_rows,
    )
