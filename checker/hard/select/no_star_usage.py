"""
硬性规则 - 禁止使用 *

触发关键字: SELECT *, COUNT(*), SUM(*)
核心目标: 禁止所有 * 用法，包括 SELECT * / COUNT(*) / SUM(*) / t.* 等
正确写法: 明确写出所有需要的字段名，COUNT(1) 替代 COUNT(*)

违规: SELECT * FROM t
违规: SELECT COUNT(*) FROM t
违规: SELECT t.* FROM t
正确: SELECT t.user_id, t.order_id FROM t
正确: SELECT COUNT(1) FROM t
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

_AGGREGATE_TYPES = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)


class NoStarUsageChecker(BaseChecker):
    rule_id = "SQL-STAR-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if not isinstance(node, exp.Star):
                    continue

                # Determine the context of the star usage
                parent = node.parent
                if isinstance(parent, exp.Select):
                    violations.append(
                        Violation(
                            message="禁止 SELECT *，请明确列出需要的字段",
                        )
                    )
                elif isinstance(parent, _AGGREGATE_TYPES):
                    violations.append(
                        Violation(
                            message="禁止在聚合函数中使用 *，请替换为具体字段或 1",
                        )
                    )
                else:
                    violations.append(
                        Violation(
                            message="禁止使用 *，请替换为具体字段",
                        )
                    )
        return violations
