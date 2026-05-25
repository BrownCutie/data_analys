"""
规范检查 - 多表查询时表和字段必须带别名

触发关键字: 表别名 (多表, JOIN, 子查询)
核心目标: 所有表必须有别名，字段引用必须带表别名前缀
正确写法: SELECT t0.user_id FROM user_table t0

违规: SELECT user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id
正确: SELECT t0.user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class TableAliasChecker(BaseChecker):
    rule_id = "SQL-TABLE-ALIAS-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            # 只在多表场景检查
            joins = list(stmt.find_all(exp.Join))
            subqueries = list(stmt.find_all(exp.Subquery))
            if not joins and not subqueries:
                continue
            for col in stmt.find_all(exp.Column):
                if not col.table:
                    violations.append(Violation(
                        rule=self.rule_id,
                        message=f"多表查询时字段 '{col.name}' 必须带表别名",
                        severity="warning",
                    ))
        return violations
