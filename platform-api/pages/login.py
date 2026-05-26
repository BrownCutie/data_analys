"""
登录模块 - 管理 cookie 的获取、检查、自动续期

使用方式:
    from login import require_login

    @require_login
    def some_api_call(...):
        ...

核心机制:
    1. check_login() 检查 cookie.json 是否存在且未过期（24小时）
    2. login() 通过 Playwright 模拟登录，保存 cookie 到 cookie.json
    3. 全局 asyncio.Lock 保证并发场景下只有一个 login() 在执行
    4. require_login 装饰器在每次 API 调用前自动检查 cookie 有效性
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from functools import wraps
from pathlib import Path

COOKIE_FILE = Path(__file__).resolve().parent.parent / "cookie.json"
COOKIE_MAX_AGE = 24 * 3600  # 24 小时，单位秒

# ── 全局登录锁，防止并发重复登录 ──────────────────────────────────
_login_lock = asyncio.Lock()


def _read_cookie() -> dict | None:
    """读取本地 cookie 文件，返回 dict 或 None"""
    if not COOKIE_FILE.exists():
        return None
    try:
        data = json.loads(COOKIE_FILE.read_text())
        return data
    except (json.JSONDecodeError, KeyError):
        return None


def check_login() -> bool:
    """
    检查 cookie 是否有效。
    有效条件：文件存在 + saved_at 字段距现在不超过 24 小时。
    """
    data = _read_cookie()
    if not data:
        return False
    saved_at = data.get("saved_at")
    if not saved_at:
        return False
    try:
        saved_time = datetime.fromisoformat(saved_at).timestamp()
        return (time.time() - saved_time) < COOKIE_MAX_AGE
    except (ValueError, OSError):
        return False


def get_cookie_header() -> str:
    """
    从 cookie.json 读取 cookie，拼成 HTTP 请求头格式。
    返回值示例: "session_id=abc123; token=xyz"
    """
    data = _read_cookie()
    if not data or "cookies" not in data:
        return ""
    return "; ".join(f"{k}={v}" for k, v in data["cookies"].items())


async def login() -> None:
    """
    通过 Playwright 模拟登录，保存 cookie 到 cookie.json。

    ⚠️ TODO: 需要根据你的平台实际情况修改以下内容：
       - 登录页面 URL
       - 用户名/密码的选择器
       - 验证码处理（如有）
       - 登录成功判断条件
    """
    from playwright.async_api import async_playwright

    LOGIN_URL = "https://your-platform.com/#/login"  # TODO: 替换为实际地址
    USERNAME = ""  # TODO: 从环境变量或配置文件读取
    PASSWORD = ""  # TODO: 从环境变量或配置文件读取

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_page()

        await context.goto(LOGIN_URL)
        await context.wait_for_load_state("networkidle")

        # TODO: 填写用户名密码
        # await context.fill('input[name="username"]', USERNAME)
        # await context.fill('input[name="password"]', PASSWORD)
        # await context.click('button[type="submit"]')
        # await context.wait_for_load_state("networkidle")

        # TODO: 验证登录成功（例如检查页面跳转或某个元素出现）
        # assert "index" in context.url, "登录失败"

        # 保存 cookie
        cookies = await context.cookies()
        cookie_dict = {c["name"]: c["value"] for c in cookies}
        _save_cookie(cookie_dict)

        await browser.close()


def _save_cookie(cookie_dict: dict) -> None:
    """保存 cookie 到文件，附带时间戳"""
    data = {
        "saved_at": datetime.now().isoformat(),
        "cookies": cookie_dict,
    }
    COOKIE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


async def ensure_login() -> None:
    """
    确保已登录（cookie 有效）。
    如果 cookie 过期，自动执行 login()。
    使用全局锁保证并发场景下只有一个 login() 在执行。

    原理（双重检查锁）:
        1. 快速路径：先不加锁检查 cookie，有效直接返回
        2. 慢路径：加锁后再检查一次（可能别的协程已经登录完了）
        3. 确实过期：执行 login()
    """
    # 快速路径：cookie 还有效，直接返回
    if check_login():
        return

    # 慢路径：加锁
    async with _login_lock:
        # 再检查一次，可能等待锁期间别的协程已经登录了
        if check_login():
            return
        await login()


def require_login(func):
    """
    装饰器：在执行 API 调用前自动检查 cookie 有效性。

    用法:
        @require_login
        async def get_table_info(table_name: str) -> dict:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers={"Cookie": get_cookie_header()})
                return resp.json()
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await ensure_login()
        return await func(*args, **kwargs)
    return wrapper
