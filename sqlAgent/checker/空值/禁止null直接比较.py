"""
禁止 NULL 直接比较

触发关键字: = NULL, != NULL, > NULL, < NULL
核心目标: 禁止对 NULL 使用 =、!=、> 等运算符，请使用 IS NULL / IS NOT NULL / NVL()
违规示例:
    SELECT * FROM orders WHERE amount = NULL
    SELECT * FROM orders WHERE status != NULL
正确写法:
    SELECT * FROM orders WHERE amount IS NULL
    SELECT * FROM orders WHERE status IS NOT NULL
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

_COMPARE_TYPES = (exp.EQ, exp.NEQ, exp.GT, exp.LT, exp.GTE, exp.LTE)


class ForbidNullCompareChecker(BaseChecker):
    rule_id = "SQL-NULL-COMPARE-001"
    name = "禁止NULL直接比较"
    desc = "禁止对 NULL 使用 =、!=、> 等运算符，请使用 IS NULL / IS NOT NULL / NVL()"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.walk():
                if not isinstance(node, _COMPARE_TYPES):
                    continue
                left = node.this
                right = node.args.get("expression")
                if isinstance(left, exp.Null) or isinstance(right, exp.Null):
                    violations.append(
                        Violation(
                            message="禁止对 NULL 使用直接比较运算符（=、!=、>、<），请使用 IS NULL / IS NOT NULL / NVL() / COALESCE()"
                        )
                    )
        return violations
