from __future__ import annotations

"""
硬性规则 - 查询必须有分区过滤

触发关键字: 查询 Hive 表/明细表
核心目标: 查询必须有分区过滤条件，禁止全表扫描
         分区字段包括 pt_d(天), pt_h(小时), pt_m(月), pt_w(周)
正确写法: WHERE pt_d = '20260101' 或 WHERE pt_h = '03'

违规: SELECT user_id FROM dwd_xxx_di
违规: SELECT * FROM (SELECT user_id FROM dwd_xxx_di) WHERE pt_d = '20260101'
正确: SELECT user_id FROM dwd_xxx_di WHERE pt_d = '20260101'
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

PARTITION_FIELDS = {"pt_d", "pt_h", "pt_m", "pt_w"}


class PartitionRequiredChecker(BaseChecker):
    rule_id = "SQL-PARTITION-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                if self._has_partition_filter(select):
                    continue
                # Only flag selects that read from a table (not trivial selects)
                if select.find(exp.From) is None and select.find(exp.Join) is None:
                    continue
                violations.append(
                    Violation(
                        message="查询缺少分区过滤，WHERE 中必须包含 pt_d / pt_h / pt_m / pt_w 条件",
                        severity="warning",
                    )
                )
        return violations

    @staticmethod
    def _has_partition_filter(select: exp.Select) -> bool:
        """Return True if any partition field appears in the WHERE clause."""
        where = select.find(exp.Where)
        if where is None:
            return False
        for col in where.find_all(exp.Column):
            if col.name in PARTITION_FIELDS:
                return True
        return False
