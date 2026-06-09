"""
硬性规则 - 消除 RIGHT JOIN

触发关键字: RIGHT JOIN
核心目标: 禁止 RIGHT JOIN，统一使用 LEFT JOIN，调整表顺序即可
正确写法: 把右表放到左边，改为 LEFT JOIN

违规: SELECT a.id FROM a RIGHT JOIN b ON a.id = b.id
正确: SELECT b.id FROM b LEFT JOIN a ON b.id = a.id
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class NoRightJoinChecker(BaseChecker):
    rule_id = "SQL-JOIN-RIGHT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.find_all(exp.Join):
                if node.args.get("side") == "RIGHT":
                    violations.append(
                        Violation(
                            message="禁止使用 RIGHT JOIN，请调整表顺序改为 LEFT JOIN",
                        )
                    )
        return violations
