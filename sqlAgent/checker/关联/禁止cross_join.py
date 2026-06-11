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
    name = "禁止笛卡尔积关联"
    desc = "检查是否使用了 CROSS JOIN。笛卡尔积会产生海量无效数据，严重影响查询性能。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for node in statement.find_all(exp.Join):
                kind = node.args.get("kind")
                if kind and kind.upper() == "CROSS":
                    violations.append(
                        Violation(message="检测到 CROSS JOIN，请确认业务必要性；如非必须，请添加关联条件改为 INNER JOIN 或 LEFT JOIN。")
                    )
        return violations
