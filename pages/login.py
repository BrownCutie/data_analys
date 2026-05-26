"""
登录模块 - 管理 cookie 的获取、检查、自动续期

核心机制:
    1. 启动时读一次 cookie.json 到内存
    2. check_login() 只比较内存中的时间戳，零磁盘 IO
    3. login() 成功后同时更新内存缓存和文件
    4. 全局 asyncio.Lock 保证并发场景下只有一个 login() 在执行
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

# ── 内存缓存 ────────────────────────────────────────────────────
# 启动时加载一次，后续 check_login 只看这个，不走磁盘
_cache_cookies: dict = {}       # cookie key-value
_cache_saved_at: float = 0.0   # 保存时间的时间戳

# ── 全局登录锁，防止并发重复登录 ──────────────────────────────────
_login_lock = asyncio.Lock()


def _load_from_disk() -> None:
    """从磁盘加载 cookie 到内存缓存"""
    global _cache_cookies, _cache_saved_at
    if not COOKIE_FILE.exists():
        return
    try:
        data = json.loads(COOKIE_FILE.read_text())
        _cache_cookies = data.get("cookies", {})
        saved_at = data.get("saved_at", "")
        _cache_saved_at = datetime.fromisoformat(saved_at).timestamp() if saved_at else 0.0
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        _cache_cookies = {}
        _cache_saved_at = 0.0


# ── 启动时加载一次 ──────────────────────────────────────────────
_load_from_disk()


def check_login() -> bool:
    """
    检查 cookie 是否有效（纯内存比较，无磁盘 IO）。
    """
    if not _cache_cookies:
        return False
    return (time.time() - _cache_saved_at) < COOKIE_MAX_AGE


def get_cookie_header() -> str:
    """
    拼成 HTTP 请求头格式（纯内存读取，无磁盘 IO）。
    返回值示例: "session_id=abc123; token=xyz"
    """
    if not _cache_cookies:
        return ""
    return "; ".join(f"{k}={v}" for k, v in _cache_cookies.items())


async def login() -> None:
    """
    通过 Playwright 模拟登录，保存 cookie 到内存 + 文件。

    ⚠️ TODO: 需要根据你的平台实际情况修改以下内容：
       - 登录页面 URL
       - 用户名/密码的选择器
       - 验证码处理（如有）
       - 登录成功判断条件
    """
    global _cache_cookies, _cache_saved_at

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

        # 保存到内存
        _cache_cookies = {c["name"]: c["value"] for c in await context.cookies()}
        _cache_saved_at = time.time()

        # 同步到磁盘
        _save_to_disk()

        await browser.close()


def _save_to_disk() -> None:
    """将内存缓存写入磁盘"""
    data = {
        "saved_at": datetime.now().isoformat(),
        "cookies": _cache_cookies,
    }
    COOKIE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


async def ensure_login() -> None:
    """
    确保已登录（cookie 有效）。
    如果 cookie 过期，自动执行 login()。
    使用全局锁保证并发场景下只有一个 login() 在执行。

    原理（双重检查锁）:
        1. 快速路径：纯内存比较，有效直接返回（纳秒级）
        2. 慢路径：加锁后再检查一次（可能别的协程已经登录完了）
        3. 确实过期：执行 login()
    """
    if check_login():
        return

    async with _login_lock:
        if check_login():
            return
        await login()


def require_login(func):
    """
    装饰器：在执行 API 调用前自动检查 cookie 有效性。
    已装饰在 common.py 的 api_get / api_post 上，页面文件无需重复使用。
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await ensure_login()
        return await func(*args, **kwargs)
    return wrapper
