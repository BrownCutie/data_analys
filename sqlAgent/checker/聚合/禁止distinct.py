"""
禁止 DISTINCT

触发关键字: DISTINCT, COUNT(DISTINCT
核心目标: 消除所有 DISTINCT 用法，包括 SELECT DISTINCT 和 COUNT(DISTINCT x)
违规示例:
    SELECT DISTINCT user_id FROM orders
    SELECT COUNT(DISTINCT user_id) FROM orders
正确写法:
    SELECT user_id FROM orders GROUP BY user_id
    SELECT COUNT(*) FROM (SELECT user_id FROM orders GROUP BY user_id) t
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class ForbidDistinctChecker(BaseChecker):
    rule_id = "SQL-DISTINCT-001"
    name = "禁止DISTINCT"
    desc = "消除所有 DISTINCT 用法，包括 SELECT DISTINCT 和 COUNT(DISTINCT x)，请改为 GROUP BY 去重"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.walk():
                if isinstance(node, exp.Distinct):
                    violations.append(
                        Violation(message="禁止使用 DISTINCT，请改为 GROUP BY 去重")
                    )
        return violations
