from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/v0")


@router.get("/status")
async def status(request: Request):
    return {
        "status": "ok",
        "version": "1.0.0",
        "browser": request.app.state.browser_manager.is_running,
    }
