from __future__ import annotations

"""
规范检查 - ORDER BY 必须有 LIMIT

触发关键字: ORDER BY
核心目标: ORDER BY 必须搭配 LIMIT 使用，避免全局排序导致全量 shuffle
正确写法: ORDER BY create_time DESC LIMIT 100

违规: SELECT * FROM t ORDER BY create_time DESC
正确: SELECT * FROM t ORDER BY create_time DESC LIMIT 100
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class OrderByLimitChecker(BaseChecker):
    rule_id = "SQL-ORDER-LIMIT-001"
    name = "排序需限条数"
    desc = "检查 ORDER BY 是否搭配了 LIMIT。无 LIMIT 的全局排序会触发全量 shuffle，资源开销很大。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                order = select.find(exp.Order)
                if order is None:
                    continue
                limit = select.find(exp.Limit)
                if limit is not None:
                    continue
                violations.append(
                    Violation(
                        message="ORDER BY 未搭配 LIMIT，请添加 LIMIT 限制返回条数。",
                    )
                )
        return violations
