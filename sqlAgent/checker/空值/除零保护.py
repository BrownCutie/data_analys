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
    name = "除法防除零"
    desc = "检查除法运算是否做了 NULL 和除零保护。未保护时可能返回 NULL 或引发运行时异常。"

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
                        message="检测到除法运算未做保护，请使用 COALESCE(x / NULLIF(y, 0), 0) 包裹。"
                    )
                )
        return violations
