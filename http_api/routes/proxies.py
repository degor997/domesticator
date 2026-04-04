from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from shared.config.models import ProxyAddRequest

router = APIRouter(prefix="/v0")


def _get_proxy_manager(request: Request):
    return request.app.state.proxy_manager


@router.get("/proxies")
async def list_proxies(request: Request):
    pm = _get_proxy_manager(request)
    return {"proxies": await pm.list_all()}


@router.post("/proxies/add")
async def add_proxy(body: ProxyAddRequest, request: Request):
    pm = _get_proxy_manager(request)
    ok = await pm.add(body.proxy_url)
    if not ok:
        raise HTTPException(status_code=409, detail="proxy_already_exists")
    return {"status": "added", "proxy_url": body.proxy_url}


@router.delete("/proxies/{proxy_url:path}")
async def delete_proxy(proxy_url: str, request: Request):
    pm = _get_proxy_manager(request)
    ok = await pm.remove(proxy_url)
    if not ok:
        raise HTTPException(status_code=404, detail="proxy_not_found")
    return {"status": "deleted", "proxy_url": proxy_url}
