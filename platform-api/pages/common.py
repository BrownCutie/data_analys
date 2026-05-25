"""
二级页面 API 的公共工具函数

每个页面文件通过 from pages.common import api_get, api_post 来发送请求，
自动带上 cookie 和 JSON headers。
"""

from __future__ import annotations

import httpx

from login import get_cookie_header

BASE_URL = "https://your-platform.com"  # TODO: 替换为平台根地址

HEADERS = {
    "Content-Type": "application/json",
}


def _headers() -> dict:
    return {**HEADERS, "Cookie": get_cookie_header()}


async def api_get(url: str, params: dict | None = None) -> dict:
    """发送 GET 请求，自动带 cookie"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        return resp.json()


async def api_post(url: str, data: dict | None = None) -> dict:
    """发送 POST 请求，自动带 cookie"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=_headers(), json=data)
        resp.raise_for_status()
        return resp.json()
