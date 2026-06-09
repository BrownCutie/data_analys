"""
禁止 RIGHT JOIN

触发关键字: RIGHT JOIN, RIGHT OUTER JOIN
核心目标: 禁止使用 RIGHT JOIN，统一使用 LEFT JOIN
违规示例:
    SELECT * FROM orders o RIGHT JOIN users u ON o.user_id = u.id
正确写法:
    SELECT * FROM users u LEFT JOIN orders o ON o.user_id = u.id
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class ForbidRightJoinChecker(BaseChecker):
    rule_id = "SQL-JOIN-RIGHT-001"
    name = "禁止RIGHT JOIN"
    desc = "禁止使用 RIGHT JOIN，请调整表顺序改为 LEFT JOIN"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.find_all(exp.Join):
                side = node.args.get("side")
                if side and side.upper() == "RIGHT":
                    violations.append(
                        Violation(message="禁止使用 RIGHT JOIN，请调整表顺序改为 LEFT JOIN")
                    )
        return violations
