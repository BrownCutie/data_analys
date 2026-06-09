"""
分区过滤

触发关键字: SELECT, WHERE, pt_d, pt_h, pt_m, pt_w
核心目标: 查询必须有分区过滤条件，禁止全表扫描
违规示例:
    SELECT * FROM orders WHERE user_id = 123
    SELECT * FROM orders
正确写法:
    SELECT * FROM orders WHERE pt_d = '2024-01-01'
    SELECT * FROM orders WHERE pt_d = '2024-01-01' AND user_id = 123
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

PARTITION_FIELDS = {"pt_d", "pt_h", "pt_m", "pt_w"}


class PartitionFilterChecker(BaseChecker):
    rule_id = "SQL-PARTITION-001"
    name = "分区过滤"
    desc = "查询必须有分区过滤条件（pt_d/pt_h/pt_m/pt_w），禁止全表扫描"

    def _has_partition_condition(self, where_clause: exp.Expression) -> bool:
        """检查 WHERE 子句中是否包含分区字段"""
        for col in where_clause.find_all(exp.Column):
            if col.name in PARTITION_FIELDS:
                return True
        return False

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for select in statement.find_all(exp.Select):
                # 检查是否有 WHERE 子句
                where_clause = select.args.get("where")
                if not where_clause:
                    violations.append(
                        Violation(
                            message="查询缺少分区过滤，WHERE 中必须包含 pt_d / pt_h / pt_m / pt_w 条件"
                        )
                    )
                    continue

                # 检查 WHERE 中是否包含分区字段
                if not self._has_partition_condition(where_clause):
                    violations.append(
                        Violation(
                            message="查询缺少分区过滤，WHERE 中必须包含 pt_d / pt_h / pt_m / pt_w 条件"
                        )
                    )
        return violations
