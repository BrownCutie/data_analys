"""
硬性规则 - 消除 DISTINCT 写法

触发关键字: DISTINCT, COUNT(DISTINCT)
核心目标: 消除所有 DISTINCT 用法，包括 SELECT DISTINCT 和 COUNT(DISTINCT x)
正确写法: 内层 GROUP BY 去重，外层 COUNT(1) 或 SELECT

违规: SELECT DISTINCT user_id FROM t
违规: SELECT COUNT(DISTINCT user_id) FROM t
正确: SELECT user_id FROM t GROUP BY user_id
正确: SELECT COUNT(1) FROM (SELECT user_id FROM t GROUP BY user_id) t0
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class NoDistinctChecker(BaseChecker):
    rule_id = "SQL-DISTINCT-001"
    name = "禁止DISTINCT"
    desc = "消除所有 DISTINCT 用法，包括 SELECT DISTINCT 和 COUNT(DISTINCT x)，请改为 GROUP BY 去重"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Distinct):
                    violations.append(
                        Violation(message="禁止使用 DISTINCT，请改为 GROUP BY 去重")
                    )
                    break
        return violations
