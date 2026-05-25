from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoRightJoinChecker(BaseChecker):
    rule_id = "SQL-JOIN-RIGHT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Join) and node.side == "RIGHT":
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止使用 RIGHT JOIN，请调整表顺序改为 LEFT JOIN",
                    ))
        return violations
