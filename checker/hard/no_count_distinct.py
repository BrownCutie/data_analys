"""
硬性规则 - 消除 COUNT(DISTINCT) 写法

触发关键字: COUNT(DISTINCT ...)
核心目标: 禁止 COUNT(DISTINCT x)，先用 GROUP BY 去重再用 COUNT(1)
正确写法: 内层 GROUP BY + 外层 COUNT(1)

违规: SELECT COUNT(DISTINCT user_id) FROM t
正确: SELECT COUNT(1) FROM (SELECT user_id FROM t GROUP BY user_id) t0
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoCountDistinctChecker(BaseChecker):

    rule_id = "SQL-COUNT-DISTINCT-001"


    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Count) and isinstance(node.this, exp.Distinct):
                    violations.append(Violation(
                                                message="禁止使用 COUNT(DISTINCT ...)，请改为内层 GROUP BY 去重 + 外层 COUNT(1)",
                    ))
        return violations
