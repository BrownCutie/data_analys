"""
平台 API MCP 服务入口

自动发现 pages/ 下所有页面文件，将每个函数注册为 MCP Tool。
Agent 看到的工具名称格式: {中文名}_{函数名}，如 表字段检查_get_table_columns
"""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

from fastmcp import FastMCP

from login import ensure_login

mcp = FastMCP("platform-api-mcp")

PAGES_DIR = Path(__file__).parent / "pages"
REGISTRY_FILE = PAGES_DIR / "page_registry.json"


def _load_registry() -> dict:
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def _register_tools() -> None:
    """自动扫描 pages/ 目录，将每个 async 函数注册为 MCP Tool"""
    registry = _load_registry()

    for cn_name, info in registry.items():
        module_name = info["file"].removesuffix(".py")
        try:
            module = importlib.import_module(f"pages.{module_name}")
        except ImportError as e:
            print(f"[WARN] 无法加载页面模块 pages.{module_name}: {e}")
            continue

        # 获取模块文档字符串作为描述
        module_doc = (inspect.getdoc(module) or info.get("description", "")).split("\n")[0]

        for name, obj in inspect.getmembers(module, inspect.iscoroutinefunction):
            if name.startswith("_"):
                continue
            # 只注册定义在该模块中的函数，过滤掉 from common import 的公共函数
            fn_module = getattr(obj, "__module__", None)
            if hasattr(obj, "__wrapped__"):
                fn_module = getattr(obj.__wrapped__, "__module__", fn_module)
            if fn_module != module.__name__:
                continue

            # 工具名: {模块名}_{函数名}，如 table_info_get_columns
            # 描述前加中文名，让 Agent 能通过中文找到对应工具
            tool_name = f"{module_name}_{name}"
            doc = f"[{cn_name}] {inspect.getdoc(obj) or ''}"
            doc = inspect.getdoc(obj) or ""

            # 动态注册为 MCP Tool
            mcp.tool(name=tool_name, description=doc)(obj)

        print(f"[INFO] 已注册页面: {cn_name} (pages.{module_name})")


_register_tools()


# ── 登录管理工具 ────────────────────────────────────────────────
@mcp.tool
async def platform_login() -> str:
    """手动触发平台登录。通常不需要调用，系统会自动检查 cookie 有效性。"""
    from login import login
    await login()
    return "登录成功，cookie 已保存"


@mcp.tool
async def platform_check_login() -> str:
    """检查当前平台登录状态（cookie 是否有效）"""
    from login import check_login
    if check_login():
        return "cookie 有效，登录状态正常"
    return "cookie 已过期或不存在，需要重新登录"


if __name__ == "__main__":
    mcp.run()
