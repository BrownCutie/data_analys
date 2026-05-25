from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class FieldAliasChecker(BaseChecker):
    rule_id = "SQL-FIELD-ALIAS-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            # 检查是否有 JOIN（多表场景）
            joins = list(stmt.find_all(exp.Join))
            subqueries = list(stmt.find_all(exp.Subquery))
            if not joins and not subqueries:
                continue
            # 遍历 SELECT 列中的 Column 节点
            for col in stmt.find_all(exp.Column):
                if not col.table:
                    violations.append(Violation(
                        rule=self.rule_id,
                        message=f"多表查询时字段 '{col.name}' 必须带表别名",
                        severity="warning",
                    ))
        return violations
