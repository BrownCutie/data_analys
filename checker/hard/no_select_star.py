"""
硬性规则 - 禁止 SELECT *

触发关键字: SELECT *
核心目标: 必须显式列出字段，不允许 SELECT *
正确写法: 明确写出所有需要的字段名

违规: SELECT * FROM t
违规: SELECT t.* FROM t
正确: SELECT t.user_id, t.order_id FROM t
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoSelectStarChecker(BaseChecker):
    rule_id = "SQL-SELECT-STAR-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            for expression in stmt.expressions:
                if isinstance(expression, exp.Star):
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止 SELECT *，请明确列出需要的字段",
                    ))
                # SELECT t.* 的情况
                elif isinstance(expression, exp.Column) and isinstance(expression.this, exp.Star):
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止 SELECT t.*，请明确列出需要的字段",
                    ))
        return violations
