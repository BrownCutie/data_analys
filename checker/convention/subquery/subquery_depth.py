from __future__ import annotations

"""
规范检查 - 子查询嵌套不超过 3 层

触发关键字: 嵌套子查询
核心目标: 子查询嵌套不能超过 3 层，过深应拆为临时表
         提高可读性和可维护性
正确写法: 使用 CREATE TABLE tmp_xxx AS SELECT ... 拆分

违规: SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM t) t0) t1) t2
正确: 逐步创建临时表，每层不超过 3 级嵌套
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

MAX_DEPTH = 3


class SubqueryDepthChecker(BaseChecker):
    rule_id = "SQL-NEST-DEPTH-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            depth = self._max_subquery_depth(stmt, 0)
            if depth > MAX_DEPTH:
                violations.append(
                    Violation(
                        message=f"子查询嵌套层级 ({depth}) 超过限制 ({MAX_DEPTH})，请拆分为临时表",
                        severity="warning",
                    )
                )
        return violations

    @staticmethod
    def _max_subquery_depth(node: exp.Expression, current_depth: int = 0) -> int:
        """Recursively compute the maximum subquery nesting depth.

        Uses find_all once at each level to get *all* nested subqueries,
        then measures depth by the nesting chain length rather than
        recursing with find_all again (which would cause infinite recursion
        since find_all is itself recursive).
        """
        all_subqueries = list(node.find_all(exp.Subquery))
        if not all_subqueries:
            return current_depth
        max_depth = current_depth
        for sq in all_subqueries:
            # Count how many ancestors of sq are also Subquery nodes
            depth = current_depth + 1
            parent = sq.parent
            while parent is not None:
                if isinstance(parent, exp.Subquery):
                    depth += 1
                parent = parent.parent
            if depth > max_depth:
                max_depth = depth
        return max_depth
