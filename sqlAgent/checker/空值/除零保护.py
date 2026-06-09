"""
除零保护

触发关键字: /, DIV, 除法
核心目标: 除法运算必须用 COALESCE(x / NULLIF(y, 0), 0) 做 NULL 和除零保护
违规示例:
    SELECT amount / total FROM orders
    SELECT SUM(amount) / COUNT(*) FROM orders
正确写法:
    SELECT COALESCE(amount / NULLIF(total, 0), 0) FROM orders
    SELECT COALESCE(SUM(amount) / NULLIF(COUNT(*), 0), 0) FROM orders
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class DivideZeroProtectionChecker(BaseChecker):
    rule_id = "SQL-NULL-ZERO-001"
    name = "除零保护"
    desc = "除法运算必须用 COALESCE(x / NULLIF(y, 0), 0) 做 NULL 和除零保护"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.walk():
                if not isinstance(node, exp.Div):
                    continue
                # 检查除法节点的父节点是否是 COALESCE
                parent = node.parent
                if isinstance(parent, exp.Coalesce):
                    continue
                violations.append(
                    Violation(
                        message="除法运算缺少 NULL 和除零保护，请使用 COALESCE(x / NULLIF(y, 0), 0)"
                    )
                )
        return violations
