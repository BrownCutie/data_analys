from __future__ import annotations

"""
硬性规则 - 除法运算必须有 NULL 和除零保护

触发关键字: 除法运算 (/, 比率, 转化率)
核心目标: 所有除法运算必须做分母为零和 NULL 的保护
         使用 NULLIF 防止除零，使用 COALESCE 处理 NULL 结果
正确写法: COALESCE(a / NULLIF(b, 0), 0)

违规: a / b
违规: a / NULLIF(b, 0)
正确: COALESCE(a / NULLIF(b, 0), 0)
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class NullZeroChecker(BaseChecker):
    rule_id = "SQL-NULL-ZERO-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if not isinstance(node, exp.Div):
                    continue
                if self._wrapped_by_coalesce(node):
                    continue
                violations.append(
                    Violation(
                        message="除法运算缺少 NULL 和除零保护，"
                        "请使用 COALESCE(x / NULLIF(y, 0), 0)",
                        severity="warning",
                    )
                )
        return violations

    @staticmethod
    def _wrapped_by_coalesce(node: exp.Expression) -> bool:
        """Walk up the parent chain to see if a Div is inside a Coalesce."""
        parent = node.parent
        while parent is not None:
            if isinstance(parent, exp.Coalesce):
                return True
            parent = parent.parent
        return False
