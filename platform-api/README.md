# 平台 API 调用 MCP

通过 Playwright 登录获取 cookie，然后调用平台各二级页面 API。每个二级页面独立一个 .py 文件，自动注册为 MCP Tool。

## 安装

```bash
cd platform-api
uv sync
uv run playwright install chromium
```

## 配置

编辑以下文件中的 TODO 项：

1. **`login.py`** — 填写登录页面 URL、用户名密码选择器
2. **`pages/common.py`** — 填写平台根地址 `BASE_URL`

## 快速验证

```bash
uv run fastmcp run server.py
```

## 目录结构

```
platform-api/
├── server.py              # MCP 入口，自动发现注册所有页面 API
├── login.py               # 登录管理（check_login / login / require_login 装饰器）
├── pages/
│   ├── common.py          # 公共请求函数（api_get / api_post）
│   ├── page_registry.json # 中文名 → .py 文件映射
│   ├── table_info.py      # 表字段信息
│   └── sql_execute.py     # SQL 执行
```

## 如何新增一个二级页面

### 第 1 步：创建页面文件

在 `pages/` 下新建 .py 文件，例如 `data_quality.py`：

```python
"""
二级页面 - 数据质量检查

页面路径: /#/data-quality
功能列表:
    1. get_quality_report  - 获取数据质量报告
    2. run_quality_check   - 触发质量检查任务

URL 前缀: {BASE_URL}/api/data-quality
"""

from __future__ import annotations

from login import require_login
from .common import BASE_URL, api_get, api_post

URL_PREFIX = f"{BASE_URL}/api/data-quality"


@require_login
async def get_quality_report(table_name: str) -> dict:
    """获取数据质量报告

    参数:
        table_name: 表名

    返回: 质量报告
    """
    url = f"{URL_PREFIX}/report"
    return await api_get(url, params={"tableName": table_name})


@require_login
async def run_quality_check(table_name: str) -> dict:
    """触发质量检查任务

    参数:
        table_name: 表名

    返回: 任务信息
    """
    url = f"{URL_PREFIX}/run"
    return await api_post(url, data={"tableName": table_name})
```

### 第 2 步：注册到 page_registry.json

```json
{
  "表字段信息": { "file": "table_info.py", "description": "获取表的字段信息" },
  "SQL执行": { "file": "sql_execute.py", "description": "提交并执行 Spark SQL" },
  "数据质量检查": { "file": "data_quality.py", "description": "数据质量检查与报告" }
}
```

完成。`server.py` 会自动发现新页面中的所有 async 函数，注册为 MCP Tool。

## MCP 客户端配置

### OpenCode

编辑 `~/.config/opencode/opencode.json`：

```json
{
  "mcp": {
    "platform-api": {
      "type": "local",
      "command": ["uv", "run", "--directory", "PROJECT_DIR/platform-api", "fastmcp", "run", "server.py"]
    }
  }
}
```

### Claude Code

项目目录下 `.mcp.json`：

```json
{
  "mcpServers": {
    "platform-api": {
      "command": "uv",
      "args": ["run", "--directory", "PROJECT_DIR/platform-api", "fastmcp", "run", "server.py"]
    }
  }
}
```

## Agent 看到的工具命名

格式：`{模块名}_{函数名}`，描述中带中文名方便 Agent 定位：

| 工具名 | 说明 |
|---|---|
| `table_info_get_table_columns` | [表字段信息] 获取表字段列表 |
| `table_info_get_table_detail` | [表字段信息] 获取表详细信息 |
| `table_info_search_tables` | [表字段信息] 按关键字搜索表名 |
| `sql_execute_submit_sql` | [SQL执行] 提交 SQL 执行任务 |
| `sql_execute_get_sql_status` | [SQL执行] 查询执行状态 |
| `sql_execute_get_sql_result` | [SQL执行] 获取执行结果 |

## 并发登录保护机制

```
请求 A 发现 cookie 过期 → 加锁 → 执行 login() → 保存 cookie → 释放锁
请求 B 发现 cookie 过期 → 等待锁 → 拿到锁 → 再检查 cookie（已更新）→ 直接返回
请求 C 发现 cookie 有效 → 直接返回（不加锁）
```

使用 `asyncio.Lock` 实现双重检查锁，确保全局只有一个 `login()` 在执行。
