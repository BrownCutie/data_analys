from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoUnionChecker(BaseChecker):
    """
    硬性规则 - 禁止 UNION（必须使用 UNION ALL）

    触发关键字: UNION (不带 ALL)
    核心目标: UNION 会隐式去重（等同于 DISTINCT），性能差且语义不清
             必须使用 UNION ALL，如需去重请显式 GROUP BY
    正确写法: UNION ALL + GROUP BY

    违规: SELECT id FROM t1 UNION SELECT id FROM t2
    正确: SELECT id FROM t1 UNION ALL SELECT id FROM t2
    正确: SELECT id FROM (SELECT id FROM t1 UNION ALL SELECT id FROM t2) GROUP BY id
    """

    rule_id = "SQL-UNION-001"
    name = "禁止UNION"
    desc = "禁止 UNION（不带 ALL），UNION 隐式去重等同于 DISTINCT，请改用 UNION ALL"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []

        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Union):
                    if node.args.get("distinct") is True:
                        violations.append(
                            Violation(
                                message="禁止使用 UNION，请改用 UNION ALL（UNION 会隐式去重，等同于 DISTINCT）",
                            )
                        )

        return violations
