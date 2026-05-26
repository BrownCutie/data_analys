"""
规范检查 - 分区过滤必须存在且下推

触发关键字: 分区过滤 (查 Hive表/明细表, 出现 pt_)
核心目标: 查询必须有分区过滤（pt_d/pt_h），禁止全表扫描
         分区条件必须在最内层/最先执行，不要在外层才过滤
正确写法: WHERE pt_d = '20260101' 或 WHERE pt_d BETWEEN '20260101' AND '20260107'

违规: SELECT user_id FROM dwd_xxx_di
违规: SELECT * FROM (SELECT user_id FROM dwd_xxx_di) WHERE pt_d = '20260101'
正确: SELECT user_id FROM dwd_xxx_di WHERE pt_d = '20260101'
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation

PARTITION_FIELDS = {"pt_d", "pt_h"}


class PartitionFilterChecker(BaseChecker):

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            columns_in_where = set()
            where = stmt.find(exp.Where)
            if where:
                for col in where.find_all(exp.Column):
                    columns_in_where.add(col.name)
            if not columns_in_where.intersection(PARTITION_FIELDS):
                violations.append(Violation(
                                        message="查询缺少分区过滤，WHERE 中必须包含 pt_d 或 pt_h 条件",
                ))
        return violations
