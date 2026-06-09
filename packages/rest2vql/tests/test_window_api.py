"""REST window endpoint tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from rest2vql.app import create_app

try:
    import imagehash  # noqa: F401

    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def _solid_image(path: Path, color: tuple[int, int, int] = (40, 80, 120)) -> Path:
    from PIL import Image

    Image.new("RGB", (64, 64), color).save(path)
    return path


def _program_with_fingerprint(path: Path, fingerprint: dict) -> Path:
    path.write_text(
        json.dumps(
            {
                "metadata": {"fingerprint": fingerprint},
                "scene": {"width": 64, "height": 64, "layers": []},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_window_detect_missing_dep(client: TestClient, tmp_path: Path) -> None:
    img = _solid_image(tmp_path / "x.png")
    try:
        from img2vql.detect import detect_ui_elements  # noqa: F401
    except ImportError:
        r = client.post("/v1/window/detect", json={"image": str(img)})
        assert r.status_code == 501
        return

    r = client.post("/v1/window/detect", json={"image": str(img), "locale": "pl"})
    assert r.status_code == 200
    assert r.json().get("ok") is True


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_window_compare(client: TestClient, tmp_path: Path) -> None:
    from img2vql.fingerprint import fingerprint_for_image

    img = _solid_image(tmp_path / "screen.png")
    fp = fingerprint_for_image(img)
    assert fp is not None
    prog = _program_with_fingerprint(tmp_path / "app.vql.json", fp)

    r = client.post("/v1/window/compare", json={"image": str(img), "file": str(prog)})
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body.get("match") is True


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_window_refresh(client: TestClient, tmp_path: Path) -> None:
    from img2vql.fingerprint import fingerprint_for_image

    img = _solid_image(tmp_path / "screen.png")
    fp = fingerprint_for_image(img)
    assert fp is not None
    prog = _program_with_fingerprint(tmp_path / "app.vql.json", fp)

    r = client.post(
        "/v1/window/refresh",
        json={"image": str(img), "file": str(prog), "locale": "en"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert "special_hits" in body


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash not installed")
def test_window_diagnose(client: TestClient, tmp_path: Path) -> None:
    img = _solid_image(tmp_path / "screen.png")
    prog = tmp_path / "app.vql.json"
    prog.write_text(
        json.dumps({"metadata": {}, "scene": {"width": 64, "height": 64, "layers": []}}),
        encoding="utf-8",
    )

    r = client.post(
        "/v1/window/diagnose",
        json={"image": str(img), "file": str(prog), "locale": "en", "save": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body.get("saved_to_program") is True
