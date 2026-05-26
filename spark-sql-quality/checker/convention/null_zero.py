"""
规范检查 - 除法/比率计算必须有 NULL 和除零保护

触发关键字: 除法/比率/金额 (计算转化率、均值等)
核心目标: 所有除法运算必须做分母为零和 NULL 的保护
         使用 NULLIF 防止除零，使用 COALESCE 处理 NULL
正确写法: COALESCE(a.click_cnt / NULLIF(b.total_cnt, 0), 0)

违规: a.click_cnt / b.total_cnt
违规: a.click_cnt / NULLIF(b.total_cnt, 0)
正确: COALESCE(a.click_cnt / NULLIF(b.total_cnt, 0), 0)
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation


class NullZeroChecker(BaseChecker):
    rule_id = "SQL-NULL-ZERO-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                # 找到除法运算
                if isinstance(node, exp.Div):
                    # 检查除法是否被 COALESCE 包裹
                    parent = node.parent
                    has_coalesce = False
                    while parent:
                        if isinstance(parent, exp.Coalesce):
                            has_coalesce = True
                            break
                        parent = parent.parent
                    if not has_coalesce:
                        violations.append(Violation(
                            rule=self.rule_id,
                            message="除法运算缺少 NULL 和除零保护，请使用 COALESCE(x / NULLIF(y, 0), 0)",
                            severity="warning",
                        ))
        return violations
