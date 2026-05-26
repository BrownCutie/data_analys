"""
规范检查 - GROUP BY 字段完整性

触发关键字: GROUP BY (出现聚合函数)
核心目标: SELECT 中的非聚合字段必须全部出现在 GROUP BY 中
         避免遗漏维度导致数据错误
正确写法: SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id, city

违规: SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id
正确: SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id, city
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation


class GroupByChecker(BaseChecker):

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            group = stmt.find(exp.Group)
            if not group:
                continue
            # 收集 GROUP BY 中的列名
            group_cols = set()
            for col in group.find_all(exp.Column):
                group_cols.add(col.name)
            # 检查 SELECT 中的非聚合列是否都在 GROUP BY 中
            for expression in stmt.expressions:
                # 跳过聚合表达式本身
                if isinstance(expression, (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)):
                    continue
                # 检查表达式中的列引用
                for col in expression.find_all(exp.Column):
                    if col.name not in group_cols:
                        violations.append(Violation(
                                                        message=f"字段 '{col.name}' 在 SELECT 中但不在 GROUP BY 中",
                            severity="warning",
                        ))
        return violations
