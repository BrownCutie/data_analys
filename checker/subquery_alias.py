from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class SubqueryAliasChecker(BaseChecker):
    rule_id = "SQL-SUBQUERY-ALIAS-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Subquery) and not node.alias:
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="子查询必须有别名，例如 FROM (SELECT ...) t0",
                    ))
        return violations
