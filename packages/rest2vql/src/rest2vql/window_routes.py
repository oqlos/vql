"""FastAPI router for window/* REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from rest2vql.window import (
    WindowImageBody,
    window_adopt,
    window_analyze,
    window_compare,
    window_detect,
    window_diagnose,
    window_refresh,
    window_summary,
)

router = APIRouter(prefix="/v1/window", tags=["window"])


def _window_response(payload: dict) -> JSONResponse:
    status = 200 if payload.get("ok", True) else 400
    return JSONResponse(payload, status_code=status)


@router.post("/detect")
def post_window_detect(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(window_detect(req.image, locale=req.locale))
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)


@router.post("/compare")
def post_window_compare(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(window_compare(req.image, file=req.file))
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)


@router.post("/refresh")
def post_window_refresh(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(window_refresh(req.image, file=req.file, locale=req.locale))
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)


@router.post("/diagnose")
def post_window_diagnose(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(
            window_diagnose(
                req.image,
                file=req.file,
                locale=req.locale,
                translate_mode=req.translate_mode,
                save=req.save,
            )
        )
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)


@router.post("/analyze")
def post_window_analyze(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(
            window_analyze(
                req.image,
                file=req.file,
                grid=req.grid,
                interactive=req.interactive,
            )
        )
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)


@router.post("/adopt")
def post_window_adopt(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(
            window_adopt(
                req.image,
                file=req.file,
                locale=req.locale,
                with_grid=req.with_grid,
                grid=req.grid,
            )
        )
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)


@router.post("/summary")
def post_window_summary(req: WindowImageBody) -> JSONResponse:
    try:
        return _window_response(
            window_summary(
                file=req.file,
                image=req.image,
                live=req.live,
                locale=req.locale,
            )
        )
    except ImportError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=501)
