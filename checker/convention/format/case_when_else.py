"""
规范检查 - CASE WHEN 必须有 ELSE

触发关键字: CASE WHEN
核心目标: CASE WHEN 必须包含 ELSE 分支，缺失 ELSE 会产生 NULL 值
         导致下游计算不符合预期
正确写法: CASE WHEN x > 0 THEN 'yes' ELSE 'no' END

违规: CASE WHEN x > 0 THEN 'yes' END
正确: CASE WHEN x > 0 THEN 'yes' ELSE 'no' END
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class CaseWhenElseChecker(BaseChecker):
    rule_id = "SQL-CASE-ELSE-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.find_all(exp.Case):
                default = node.args.get("default")
                if default is None:
                    violations.append(
                        Violation(
                            message="CASE WHEN 必须包含 ELSE 分支，缺失 ELSE 会产生 NULL",
                            severity="warning",
                        )
                    )
        return violations
