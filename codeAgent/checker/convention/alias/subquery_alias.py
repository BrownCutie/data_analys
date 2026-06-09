"""
规范检查 - 子查询必须有别名

触发关键字: 子查询 (FROM/JOIN 后有嵌套 SELECT)
核心目标: 所有子查询必须有表别名
正确写法: FROM (SELECT ...) t0

违规: SELECT * FROM (SELECT user_id FROM t)
正确: SELECT * FROM (SELECT user_id FROM t) t0
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class SubqueryAliasChecker(BaseChecker):
    rule_id = "SQL-SUBQUERY-ALIAS-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.find_all(exp.Subquery):
                alias = node.args.get("alias")
                if not alias:
                    violations.append(
                        Violation(
                            message="子查询必须有别名，例如 FROM (SELECT ...) t0",
                        )
                    )
        return violations
