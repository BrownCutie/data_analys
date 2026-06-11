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
    name = "限制子查询嵌套"
    desc = "检查子查询嵌套是否超过 3 层。嵌套过深难以阅读和维护，容易引入隐藏错误。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            depth = self._max_subquery_depth(stmt, 0)
            if depth > MAX_DEPTH:
                violations.append(
                    Violation(
                        message=f"子查询嵌套 {depth} 层，超过上限 {MAX_DEPTH} 层，请拆分为中间临时表分步处理。",
                    )
                )
        return violations

    @staticmethod
    def _max_subquery_depth(node: exp.Expression, current_depth: int = 0) -> int:
        """Recursively compute the maximum subquery nesting depth.

        Traverses manually: for each Select, looks at its direct children
        for Subquery nodes, then recurses into those Subquery's Select.
        Does NOT use find_all which is recursive and would over-count.
        """
        max_depth = current_depth
        # Find direct Subquery children only (not recursive)
        for child in node.iter_expressions():
            if isinstance(child, exp.Subquery):
                depth = current_depth + 1
                # Recurse into the Subquery's inner Select
                inner = child.this
                if isinstance(inner, exp.Select):
                    inner_depth = SubqueryDepthChecker._max_subquery_depth(inner, depth)
                    if inner_depth > max_depth:
                        max_depth = inner_depth
                else:
                    if depth > max_depth:
                        max_depth = depth
            elif isinstance(child, exp.Select):
                # Recurse into nested Select statements
                inner_depth = SubqueryDepthChecker._max_subquery_depth(child, current_depth)
                if inner_depth > max_depth:
                    max_depth = inner_depth
        return max_depth
