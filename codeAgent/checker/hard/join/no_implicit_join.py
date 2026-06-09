"""
硬性规则 - 禁止隐式 JOIN

触发关键字: FROM a, b WHERE a.id = b.id
核心目标: 禁止用逗号分隔多表 + WHERE 条件关联，必须用显式 JOIN ... ON
正确写法: 显式 JOIN ... ON

违规: SELECT a.id FROM a, b WHERE a.id = b.id
正确: SELECT a.id FROM a JOIN b ON a.id = b.id
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class NoImplicitJoinChecker(BaseChecker):
    rule_id = "SQL-JOIN-IMPLICIT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.find_all(exp.Join):
                kind = node.args.get("kind")
                on = node.args.get("on")
                using = node.args.get("using")
                if kind == "CROSS" and not on and not using:
                    violations.append(
                        Violation(
                            message="禁止隐式 JOIN（FROM a, b），请改为显式 JOIN ... ON",
                        )
                    )
        return violations
