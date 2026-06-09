"""
禁止星号

触发关键字: SELECT *, COUNT(*), SUM(*)
核心目标: 禁止所有 * 用法，包括 SELECT * / COUNT(*) / SUM(*) / t.* 等
违规示例:
    SELECT * FROM orders
    SELECT COUNT(*) FROM orders
    SELECT t.* FROM orders t
正确写法:
    SELECT order_id, user_id FROM orders
    SELECT COUNT(1) FROM orders
    SELECT t.order_id, t.user_id FROM orders t
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

_AGGREGATE_TYPES = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)


class ForbidStarChecker(BaseChecker):
    rule_id = "SQL-STAR-001"
    name = "禁止星号"
    desc = "禁止所有 * 用法，包括 SELECT * / COUNT(*) / SUM(*) / t.* 等，请明确列出字段"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.walk():
                if not isinstance(node, exp.Star):
                    continue

                parent = node.parent

                if isinstance(parent, exp.Select):
                    violations.append(
                        Violation(message="禁止 SELECT *，请明确列出需要的字段")
                    )
                elif isinstance(parent, _AGGREGATE_TYPES):
                    violations.append(
                        Violation(message="禁止在聚合函数中使用 *，请替换为具体字段或 1")
                    )
                else:
                    violations.append(
                        Violation(message="禁止使用 *，请替换为具体字段")
                    )
        return violations
