"""
硬性规则 - 消除 COUNT(*) 写法

触发关键字: COUNT(*)
核心目标: 禁止 COUNT(*)，统一使用 COUNT(1)
正确写法: COUNT(1)

违规: SELECT COUNT(*) FROM t
正确: SELECT COUNT(1) FROM t
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation


class NoCountStarChecker(BaseChecker):
    rule_id = "SQL-COUNT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Count) and isinstance(node.this, exp.Star):
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止使用 COUNT(*)，请改为 COUNT(1)",
                    ))
        return violations
