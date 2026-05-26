from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoInSubqueryChecker(BaseChecker):
    """
    硬性规则 - 禁止 IN 子查询

    触发关键字: IN (SELECT ...)
    核心目标: IN 子查询在 Spark 中容易导致 BroadcastNestedLoopJoin，性能差
             应改用 JOIN 或 EXISTS 实现
    正确写法: 使用 JOIN 或 WHERE EXISTS 代替

    违规: SELECT * FROM t1 WHERE id IN (SELECT id FROM t2)
    正确: SELECT t1.* FROM t1 INNER JOIN t2 ON t1.id = t2.id
    正确: SELECT * FROM t1 WHERE EXISTS (SELECT 1 FROM t2 WHERE t2.id = t1.id)
    """

    rule_id = "SQL-IN-SUBQUERY-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []

        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.In):
                    if node.args.get("query") is not None:
                        violations.append(
                            Violation(
                                message="禁止使用 IN (SELECT ...) 子查询，请改用 JOIN 或 EXISTS",
                            )
                        )

        return violations
