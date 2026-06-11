from __future__ import annotations

"""
硬性规则 - 禁止 WITH CTE

触发关键字: WITH ... AS (SELECT ...)
核心目标: SparkSQL 必须使用临时表，禁止 WITH CTE 写法
正确写法: 使用 CREATE TABLE tmp_xxx AS SELECT ... 代替

违规: WITH t0 AS (SELECT user_id FROM user_table) SELECT * FROM t0
正确: CREATE TABLE tmp_user_20260101 AS SELECT user_id FROM user_table;
      SELECT * FROM tmp_user_20260101
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class NoCteChecker(BaseChecker):
    rule_id = "SQL-CTE-001"
    name = "不使用 WITH 语句"
    desc = "检查是否使用了 WITH 子句（CTE）。CTE 不利于任务排查和数据复用，团队规范要求改用物理临时表。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            if stmt.find(exp.With):
                violations.append(
                    Violation(
                        message="检测到 WITH CTE 语法，请改写为 CREATE TABLE tmp_{描述}_{日期} AS SELECT ... 形式的临时表。"
                    )
                )
        return violations
