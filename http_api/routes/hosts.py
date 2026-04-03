from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from shared.config.models import HostConfig

router = APIRouter(prefix="/v0/config")


def _get_store(request: Request):
    return request.app.state.config_store


@router.get("/hosts")
async def get_all_hosts(request: Request):
    store = _get_store(request)
    all_configs = await store.get_all()
    result = {}
    for hostname, strategies in all_configs.items():
        result[hostname] = {s: c.model_dump() for s, c in strategies.items()}
    return result


@router.get("/hosts/{hostname}")
async def get_host(hostname: str, request: Request):
    store = _get_store(request)
    host = await store.get_host(hostname)
    if host is None:
        raise HTTPException(status_code=404, detail="host_not_found")
    return {s: c.model_dump() for s, c in host.items()}


@router.get("/hosts/{hostname}/strategies")
async def get_host_strategies(hostname: str, request: Request):
    store = _get_store(request)
    strategies = await store.get_strategies(hostname)
    if not strategies:
        raise HTTPException(status_code=404, detail="host_not_found")
    return {"strategies": strategies}


@router.post("/hosts/{hostname}")
async def add_host_config(hostname: str, config: HostConfig, request: Request, strategy: str = "default"):
    store = _get_store(request)

    # Check if exists and frozen
    existing = await store.get_config(hostname, strategy)
    if existing and existing.frozen:
        return JSONResponse(status_code=423, content={"detail": "host_config_frozen"})

    ok = await store.add_config(hostname, strategy, config)
    if not ok:
        raise HTTPException(status_code=409, detail="host_config_exists")
    return {"status": "created", "hostname": hostname, "strategy": strategy}


@router.put("/hosts/{hostname}")
async def update_host_config(hostname: str, config: HostConfig, request: Request, strategy: str = "default"):
    store = _get_store(request)

    existing = await store.get_config(hostname, strategy)
    if existing and existing.frozen:
        return JSONResponse(status_code=423, content={"detail": "host_config_frozen"})

    ok = await store.update_config(hostname, strategy, config)
    if not ok:
        raise HTTPException(status_code=404, detail="host_config_not_found")
    return {"status": "updated", "hostname": hostname, "strategy": strategy}


@router.delete("/hosts/{hostname}")
async def delete_host_config(hostname: str, request: Request, strategy: str | None = None):
    store = _get_store(request)

    if strategy:
        existing = await store.get_config(hostname, strategy)
        if existing and existing.frozen:
            return JSONResponse(status_code=423, content={"detail": "host_config_frozen"})
    else:
        host = await store.get_host(hostname)
        if host:
            for cfg in host.values():
                if cfg.frozen:
                    return JSONResponse(status_code=423, content={"detail": "host_config_frozen"})

    ok = await store.delete_config(hostname, strategy)
    if not ok:
        raise HTTPException(status_code=404, detail="host_config_not_found")
    return {"status": "deleted", "hostname": hostname}
