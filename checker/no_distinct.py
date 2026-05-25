from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoDistinctChecker(BaseChecker):
    rule_id = "SQL-DISTINCT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Distinct):
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止使用 DISTINCT，请改为 GROUP BY 去重",
                    ))
        return violations
