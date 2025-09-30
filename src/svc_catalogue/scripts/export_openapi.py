"""Utility to export the OpenAPI specification to disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from svc_catalogue.main import app


def export_openapi(
    path: Optional[str] = "openapi.json",
) -> Path:  # pragma: no cover - tooling hook
    target = Path(path or "openapi.json").resolve()
    spec = app.openapi()
    target.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    import argparse

    parser = argparse.ArgumentParser(description="Export OpenAPI specification")
    parser.add_argument(
        "--output", "-o", default="openapi.json", help="Output file path"
    )
    args = parser.parse_args()
    exported = export_openapi(args.output)
    print(f"OpenAPI spec written to {exported}")
