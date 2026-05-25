from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

PARTITION_FIELDS = {"pt_d", "pt_h"}


class RequirePartitionFilterChecker(BaseChecker):
    rule_id = "SQL-PARTITION-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            # 收集 WHERE 中引用的所有列名
            columns_in_where = set()
            where = stmt.find(exp.Where)
            if where:
                for col in where.find_all(exp.Column):
                    columns_in_where.add(col.name)
            if not columns_in_where.intersection(PARTITION_FIELDS):
                violations.append(Violation(
                    rule=self.rule_id,
                    message="查询缺少分区过滤，WHERE 中必须包含 pt_d 或 pt_h 条件",
                ))
        return violations
