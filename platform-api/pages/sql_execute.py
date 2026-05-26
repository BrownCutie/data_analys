"""
二级页面 - SQL执行

页面路径: /#/sql-execute
功能列表:
    1. submit_sql       - 提交 SQL 执行任务
    2. get_sql_status   - 查询 SQL 执行状态
    3. get_sql_result   - 获取 SQL 执行结果

URL 前缀: {BASE_URL}/api/sql-execute
"""

from __future__ import annotations

from .common import BASE_URL, api_get, api_post

# ── 本页面的 URL 前缀 ──────────────────────────────────────────
URL_PREFIX = f"{BASE_URL}/api/sql-execute"


async def submit_sql(sql: str, database: str = "default") -> dict:
    """
    提交 SQL 执行任务

    参数:
        sql:      要执行的 SQL
        database: 使用的数据库，默认 "default"

    返回: 任务 ID 等信息
    """
    url = f"{URL_PREFIX}/submit"
    return await api_post(url, data={"sql": sql, "database": database})


async def get_sql_status(task_id: str) -> dict:
    """
    查询 SQL 执行状态

    参数:
        task_id: submit_sql 返回的任务 ID

    返回: 状态信息 (running / success / failed)
    """
    url = f"{URL_PREFIX}/status"
    return await api_get(url, params={"taskId": task_id})


async def get_sql_result(task_id: str) -> dict:
    """
    获取 SQL 执行结果

    参数:
        task_id: 任务 ID

    返回: 执行结果数据
    """
    url = f"{URL_PREFIX}/result"
    return await api_get(url, params={"taskId": task_id})
