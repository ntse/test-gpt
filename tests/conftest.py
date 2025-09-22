import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("AUTH_TOKEN", "test-token")
os.environ.setdefault("ENVIRONMENT", "test")

from sqlalchemy import delete

from svc_catalogue.db import get_session, init_db
from svc_catalogue.main import app  # noqa: E402  (import after env setup)
from svc_catalogue.models import Service


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def clean_database() -> None:
    init_db()
    with get_session() as session:
        session.exec(delete(Service))
