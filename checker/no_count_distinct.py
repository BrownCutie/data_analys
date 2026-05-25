from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoCountDistinctChecker(BaseChecker):
    rule_id = "SQL-COUNT-DISTINCT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Count) and isinstance(node.this, exp.Distinct):
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止使用 COUNT(DISTINCT ...)，请改为内层 GROUP BY 去重 + 外层 COUNT(1)",
                    ))
        return violations
