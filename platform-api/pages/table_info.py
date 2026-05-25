"""
二级页面 - 表字段检查

页面路径: /#/table-info
功能列表:
    1. get_table_columns    - 查询表的字段列表（字段名、类型、注释）
    2. get_table_detail     - 查询表的详细信息（分区、存储格式、行数）
    3. search_tables        - 按关键字搜索表名

URL 前缀: {BASE_URL}/api/table-info
"""

from __future__ import annotations

from login import require_login
from pages.common import BASE_URL, api_get, api_post

# ── 本页面的 URL 前缀 ──────────────────────────────────────────
URL_PREFIX = f"{BASE_URL}/api/table-info"


@require_login
async def get_table_columns(database: str, table_name: str) -> dict:
    """
    查询表的字段列表

    参数:
        database:    数据库名，如 "dwd"
        table_name:  表名，如 "dwd_user_click_di"

    返回: 字段列表，包含 name, type, comment 等字段
    """
    url = f"{URL_PREFIX}/columns"
    return await api_get(url, params={"database": database, "tableName": table_name})


@require_login
async def get_table_detail(database: str, table_name: str) -> dict:
    """
    查询表的详细信息（分区、存储格式、行数等）

    参数:
        database:    数据库名
        table_name:  表名

    返回: 表的详细信息
    """
    url = f"{URL_PREFIX}/detail"
    return await api_get(url, params={"database": database, "tableName": table_name})


@require_login
async def search_tables(keyword: str) -> dict:
    """
    按关键字搜索表名

    参数:
        keyword: 搜索关键字

    返回: 匹配的表列表
    """
    url = f"{URL_PREFIX}/search"
    return await api_post(url, data={"keyword": keyword})
