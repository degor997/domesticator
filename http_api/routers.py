from __future__ import annotations

from fastapi import FastAPI

from http_api.routes import base, crawl, hosts, proxies, status


def register_routers(app: FastAPI) -> None:
    app.include_router(base.router)
    app.include_router(status.router)
    app.include_router(hosts.router)
    app.include_router(proxies.router)
    app.include_router(crawl.router)
