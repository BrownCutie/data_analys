"""
规范检查 - 子查询必须有别名

触发关键字: 子查询 (FROM/JOIN 后有嵌套 SELECT)
核心目标: 所有子查询必须有表别名，且多个子查询别名符合顺序约定（t0, t1, t2...）
正确写法: FROM (SELECT ...) t0

违规: SELECT * FROM (SELECT user_id FROM t)
正确: SELECT * FROM (SELECT user_id FROM t) t0
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation


class SubqueryAliasChecker(BaseChecker):

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Subquery) and not node.alias:
                    violations.append(Violation(
                                                message="子查询必须有别名，例如 FROM (SELECT ...) t0",
                    ))
        return violations
