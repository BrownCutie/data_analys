from __future__ import annotations

"""
规范检查 - JOIN 前必须先过滤

触发关键字: JOIN 过滤 (JOIN 大表/明细表)
核心目标: 大表 JOIN 前必须先过滤（子查询内先 WHERE），避免先 JOIN 全量数据再过滤
正确写法: JOIN (SELECT ... FROM t WHERE pt_d = 'xxx') t0 ON ...

违规: SELECT a.id FROM big_table a JOIN detail_table b ON a.id = b.id WHERE a.pt_d = '20260101'
正确: SELECT a.id FROM (SELECT * FROM big_table WHERE pt_d = '20260101') a JOIN detail_table b ON a.id = b.id
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

PARTITION_FIELDS = {"pt_d", "pt_h", "pt_m", "pt_w"}


class JoinFilterFirstChecker(BaseChecker):
    rule_id = "SQL-JOIN-FILTER-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                # Only check SELECTs that have direct JOINs (from args, not nested)
                joins = select.args.get("joins")
                if not joins:
                    continue

                # Use args.get to get the WHERE that is a direct child of this
                # SELECT, not a WHERE inside a nested subquery
                where = select.args.get("where")
                if where is None:
                    continue

                # Check if the outer WHERE references partition fields
                for col in where.find_all(exp.Column):
                    if col.name in PARTITION_FIELDS:
                        violations.append(
                            Violation(
                                message="分区过滤条件未下推，建议将分区过滤移到 JOIN 前的子查询中",
                                severity="warning",
                            )
                        )
                        break  # One violation per SELECT is enough
        return violations
