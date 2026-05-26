# CLAUDE.md — 项目上下文

## 项目简介
平台 API 调用 MCP 服务。通过 Playwright 模拟登录获取 cookie，然后调用平台各二级页面 API。每个二级页面独立一个 .py 文件，自动注册为 MCP Tool。

## 技术栈
- Python + FastMCP + httpx + Playwright
- uv 管理依赖

## 目录结构
```
server.py              # MCP 入口，自动发现注册所有页面 API
pages/
├── login.py           # 登录管理（cookie 检查 / Playwright 登录 / 并发锁）
├── common.py          # api_get/api_post（带 @require_login，自动带 cookie）
├── page_registry.json # 中文名 → .py 文件映射
├── table_info.py      # 表字段信息
└── sql_execute.py     # SQL 执行
```

## 核心设计
- **登录透明**：`@require_login` 装饰器在 `common.py` 的 `api_get`/`api_post` 上，页面文件不用管登录
- **cookie 内存缓存**：启动时读一次 cookie.json 到内存，后续 check_login 零磁盘 IO
- **并发安全**：asyncio.Lock 双重检查锁，多个协程同时发现过期也只登录一次
- **自动注册**：server.py 扫描 page_registry.json，自动发现页面中的 async 函数注册为 MCP Tool

## 新增二级页面
1. 在 pages/ 下新建 .py 文件，写 async 函数，调用 api_get/api_post
2. 在 page_registry.json 中加一行映射
3. 不用改 server.py

## 页面文件模板
```python
"""
二级页面 - 页面中文名

页面路径: /#/xxx
功能列表:
    1. func_name - 功能说明

URL 前缀: {BASE_URL}/api/xxx
"""
from __future__ import annotations
from .common import BASE_URL, api_get, api_post

URL_PREFIX = f"{BASE_URL}/api/xxx"

async def func_name(param: str) -> dict:
    """功能说明"""
    url = f"{URL_PREFIX}/endpoint"
    return await api_get(url, params={"param": param})
```

## 需要配置的 TODO
- `pages/login.py`：填写登录 URL、用户名密码选择器
- `pages/common.py`：填写 BASE_URL

## 常用命令
```bash
uv sync                                    # 安装依赖
uv run playwright install chromium         # 安装浏览器
uv run fastmcp run server.py               # 启动 MCP 服务
```
