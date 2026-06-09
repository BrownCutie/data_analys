"""
禁止隐式 JOIN

触发关键字: FROM a, b WHERE
核心目标: 禁止用逗号分隔多表，请改为显式 JOIN ... ON
违规示例:
    SELECT * FROM orders o, users u WHERE o.user_id = u.id
正确写法:
    SELECT * FROM orders o JOIN users u ON o.user_id = u.id
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class ForbidImplicitJoinChecker(BaseChecker):
    rule_id = "SQL-JOIN-IMPLICIT-001"
    name = "禁止隐式JOIN"
    desc = "禁止用逗号分隔多表（FROM a, b WHERE），请改为显式 JOIN ... ON"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.find_all(exp.Join):
                kind = node.args.get("kind")
                on_clause = node.args.get("on")
                using_clause = node.args.get("using")
                if kind and kind.upper() == "CROSS" and not on_clause and not using_clause:
                    violations.append(
                        Violation(message="禁止隐式 JOIN（FROM a, b），请改为显式 JOIN ... ON")
                    )
        return violations
