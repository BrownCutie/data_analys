"""
二级页面 API 的公共工具函数

所有请求自动带 cookie，自动检查登录状态。
页面文件只需: from .common import BASE_URL, api_get, api_post
"""

from __future__ import annotations

import httpx

from .login import require_login, get_cookie_header

BASE_URL = "https://your-platform.com"  # TODO: 替换为平台根地址

HEADERS = {
    "Content-Type": "application/json",
}


def _headers() -> dict:
    return {**HEADERS, "Cookie": get_cookie_header()}


@require_login
async def api_get(url: str, params: dict | None = None) -> dict:
    """发送 GET 请求，自动带 cookie，自动检查登录"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        return resp.json()


@require_login
async def api_post(url: str, data: dict | None = None) -> dict:
    """发送 POST 请求，自动带 cookie，自动检查登录"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=_headers(), json=data)
        resp.raise_for_status()
        return resp.json()
