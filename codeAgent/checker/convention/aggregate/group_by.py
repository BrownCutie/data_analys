from __future__ import annotations

"""
规范检查 - GROUP BY 字段完整性

触发关键字: GROUP BY (出现聚合函数)
核心目标: SELECT 中的非聚合字段必须全部出现在 GROUP BY 中
         避免遗漏维度导致数据错误
正确写法: SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id, city

违规: SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id
正确: SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id, city
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

AGGREGATE_FUNCS = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)


class GroupByChecker(BaseChecker):
    rule_id = "SQL-GROUP-BY-001"
    name = "GROUP BY完整性"
    desc = "SELECT 中的非聚合字段必须全部出现在 GROUP BY 中"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                group = select.find(exp.Group)
                if group is None:
                    continue

                group_columns = self._collect_group_columns(group)

                for expr in select.expressions:
                    if self._is_aggregate_expr(expr):
                        continue
                    for col in expr.find_all(exp.Column):
                        if col.name not in group_columns:
                            violations.append(
                                Violation(
                                    message=f"字段 '{col.name}' 在 SELECT 中但不在 GROUP BY 中",
                                    severity="warning",
                                )
                            )
        return violations

    @staticmethod
    def _collect_group_columns(group: exp.Group) -> set[str]:
        """Collect all column names that appear in the GROUP BY clause."""
        columns: set[str] = set()
        for expr in group.expressions:
            for col in expr.find_all(exp.Column):
                columns.add(col.name)
        return columns

    @staticmethod
    def _is_aggregate_expr(expr: exp.Expression) -> bool:
        """Check whether the top-level expression is an aggregate function call."""
        if isinstance(expr, AGGREGATE_FUNCS):
            return True
        # Handle alias wrapping an aggregate: e.g. COUNT(1) AS cnt
        if isinstance(expr, exp.Alias):
            inner = expr.this
            if isinstance(inner, AGGREGATE_FUNCS):
                return True
        return False
