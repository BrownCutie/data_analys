"""
规范检查 - JOIN 前必须先过滤

触发关键字: JOIN 过滤 (JOIN 大表/明细表)
核心目标: 大表 JOIN 前必须先过滤（子查询内先 WHERE），避免先 JOIN 全量数据再过滤
正确写法: JOIN (SELECT ... FROM t WHERE pt_d = 'xxx') t0 ON ...

违规: SELECT a.id FROM big_table a JOIN detail_table b ON a.id = b.id WHERE a.pt_d = '20260101'
正确: SELECT a.id FROM (SELECT * FROM big_table WHERE pt_d = '20260101') a JOIN detail_table b ON a.id = b.id
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation


class JoinFilterFirstChecker(BaseChecker):

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            joins = list(stmt.find_all(exp.Join))
            if not joins:
                continue
            # 检查外层 WHERE 中是否有分区过滤
            where = stmt.find(exp.Where)
            if not where:
                continue
            partition_cols_in_where = set()
            for col in where.find_all(exp.Column):
                if col.name in ("pt_d", "pt_h"):
                    partition_cols_in_where.add(col.name)
            # 如果外层 WHERE 有分区过滤，说明过滤没有下推到子查询
            if partition_cols_in_where:
                violations.append(Violation(
                                        message="分区过滤条件未下推，建议将分区过滤移到 JOIN 前的子查询中",
                    severity="warning",
                ))
        return violations
