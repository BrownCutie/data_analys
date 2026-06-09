"""
硬性规则 - 禁止 CROSS JOIN

触发关键字: CROSS JOIN
核心目标: 禁止显式 CROSS JOIN，笛卡尔积通常不是业务需要
正确写法: 使用 INNER JOIN 或 LEFT JOIN 并指定关联条件

违规: SELECT a.id FROM a CROSS JOIN b
正确: SELECT a.id FROM a INNER JOIN b ON a.id = b.id
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class NoCrossJoinChecker(BaseChecker):
    rule_id = "SQL-CROSS-JOIN-001"
    name = "禁止CROSS JOIN"
    desc = "禁止显式 CROSS JOIN，笛卡尔积通常不是业务需要"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.find_all(exp.Join):
                if node.args.get("kind") == "CROSS":
                    violations.append(
                        Violation(
                            message="禁止使用 CROSS JOIN，笛卡尔积会导致性能问题",
                        )
                    )
        return violations
