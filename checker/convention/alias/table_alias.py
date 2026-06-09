"""
规范检查 - 多表查询时表和字段必须带别名

触发关键字: 多表, JOIN, 子查询
核心目标: 所有表必须有别名，字段引用必须带表别名前缀
正确写法: SELECT t0.user_id FROM user_table t0

违规: SELECT user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id
正确: SELECT t0.user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class TableAliasChecker(BaseChecker):
    rule_id = "SQL-TABLE-ALIAS-001"
    name = "表别名"
    desc = "多表/JOIN/子查询时，字段引用必须带表别名前缀"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                if not self._is_multi_table(select):
                    continue
                for col in select.find_all(exp.Column):
                    if not col.table:
                        violations.append(
                            Violation(
                                message=f"多表查询时字段 '{col.name}' 必须带表别名",
                                severity="warning",
                            )
                        )
        return violations

    @staticmethod
    def _is_multi_table(select: exp.Select) -> bool:
        """Check if a SELECT involves multiple tables (JOINs or subqueries)."""
        joins = list(select.find_all(exp.Join))
        if joins:
            return True
        # Check for subqueries in FROM
        from_clause = select.find(exp.From)
        if from_clause:
            for subq in from_clause.find_all(exp.Subquery):
                return True
        # Check for multiple tables in FROM (comma-separated)
        if from_clause:
            tables = list(from_clause.find_all(exp.Table))
            if len(tables) > 1:
                return True
        return False
