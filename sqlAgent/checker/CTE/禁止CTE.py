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
    name = "禁止CTE"
    desc = "禁止 WITH CTE，请改用临时表（CREATE TABLE tmp_xxx AS SELECT ...）"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            if stmt.find(exp.With):
                violations.append(
                    Violation(
                        message="禁止使用 WITH CTE，请改用临时表"
                        "（CREATE TABLE tmp_xxx AS SELECT ...）"
                    )
                )
        return violations
