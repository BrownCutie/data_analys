from __future__ import annotations

"""
规范检查 - 子查询必须有别名

触发关键字: 子查询 (FROM/JOIN 后有嵌套 SELECT)
核心目标: 所有子查询必须有表别名
正确写法: FROM (SELECT ...) t0

违规: SELECT * FROM (SELECT user_id FROM t)
正确: SELECT * FROM (SELECT user_id FROM t) t0
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class SubqueryAliasChecker(BaseChecker):
    rule_id = "SQL-SUBQUERY-ALIAS-001"
    name = "子查询需加别名"
    desc = "检查 FROM 子句中的子查询是否定义了表别名。无别名时无法引用子查询字段。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.find_all(exp.Subquery):
                alias = node.args.get("alias")
                if not alias:
                    violations.append(
                        Violation(
                            message="子查询缺少表别名，请添加别名，如 FROM (SELECT ...) AS t0。",
                        )
                    )
        return violations
