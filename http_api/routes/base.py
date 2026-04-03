from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"


@router.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")


@router.get("/ping")
async def ping():
    return {"ping": "pong"}


@router.get("/health")
async def health():
    return {"status": "ok"}
