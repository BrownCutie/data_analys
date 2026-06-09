"""
禁止 CROSS JOIN

触发关键字: CROSS JOIN
核心目标: 禁止显式 CROSS JOIN，笛卡尔积通常不是业务需要
违规示例:
    SELECT * FROM orders CROSS JOIN users
正确写法:
    -- 如果确实需要笛卡尔积，请添加明确的业务注释说明原因
    SELECT /* CROSS JOIN: 说明原因 */ * FROM orders CROSS JOIN users
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class ForbidCrossJoinChecker(BaseChecker):
    rule_id = "SQL-CROSS-JOIN-001"
    name = "禁止CROSS JOIN"
    desc = "禁止显式 CROSS JOIN，笛卡尔积通常不是业务需要"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.find_all(exp.Join):
                kind = node.args.get("kind")
                if kind and kind.upper() == "CROSS":
                    violations.append(
                        Violation(message="禁止使用 CROSS JOIN，笛卡尔积会导致性能问题")
                    )
        return violations
