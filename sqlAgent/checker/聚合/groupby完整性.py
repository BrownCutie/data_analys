"""
GROUP BY 完整性

触发关键字: SELECT, GROUP BY
核心目标: SELECT 中的非聚合字段必须全部出现在 GROUP BY 中
违规示例:
    SELECT user_id, order_id, COUNT(*) FROM orders GROUP BY user_id
正确写法:
    SELECT user_id, order_id, COUNT(*) FROM orders GROUP BY user_id, order_id
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

_AGGREGATE_TYPES = (
    exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max,
    exp.ApproxDistinct, exp.ArrayAgg, exp.CountIf,
)


class GroupByCompletenessChecker(BaseChecker):
    rule_id = "SQL-GROUP-BY-001"
    name = "GROUP BY 字段完整"
    desc = "检查 SELECT 中的非聚合字段是否都出现在 GROUP BY 中。遗漏会导致结果不正确或执行报错。"

    def _contains_aggregate(self, node: exp.Expression) -> bool:
        """判断表达式中是否包含聚合函数"""
        for child in node.find_all(*_AGGREGATE_TYPES):
            if child is not node:
                return True
        return isinstance(node, _AGGREGATE_TYPES)

    def _get_group_by_columns(self, select: exp.Select) -> set[str]:
        """提取 GROUP BY 中的列名"""
        group = select.args.get("group")
        if not group:
            return set()
        columns: set[str] = set()
        for expr in group.expressions:
            for col in expr.find_all(exp.Column):
                columns.add(col.name)
        return columns

    def _get_select_columns(self, select: exp.Select) -> list[exp.Column]:
        """提取 SELECT 中的非聚合列"""
        columns: list[exp.Column] = []
        for expr in select.expressions:
            if isinstance(expr, (exp.Star, exp.Column)):
                if isinstance(expr, exp.Column) and not self._contains_aggregate(expr):
                    columns.append(expr)
                elif isinstance(expr, exp.Star):
                    # SELECT * 在 GROUP BY 中一定是不完整的
                    columns.append(expr)
            elif isinstance(expr, exp.Alias):
                inner = expr.this
                if isinstance(inner, exp.Column) and not self._contains_aggregate(inner):
                    columns.append(inner)
        return columns

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for select in statement.find_all(exp.Select):
                group = select.args.get("group")
                if not group:
                    continue

                group_cols = self._get_group_by_columns(select)
                select_cols = self._get_select_columns(select)

                for col in select_cols:
                    if col.name not in group_cols:
                        violations.append(
                            Violation(
                                message=f"字段 '{col.name}' 出现在 SELECT 中但未包含在 GROUP BY，请补入 GROUP BY 或改为聚合函数。"
                            )
                        )
        return violations
