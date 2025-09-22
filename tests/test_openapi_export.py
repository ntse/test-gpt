from pathlib import Path

from svc_catalogue.scripts.export_openapi import export_openapi


def test_export_openapi(tmp_path: Path) -> None:
    output = tmp_path / "openapi.json"
    result_path = export_openapi(str(output))
    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "openapi" in content
