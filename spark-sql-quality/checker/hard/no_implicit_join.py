"""
硬性规则 - 禁止隐式 JOIN

触发关键字: FROM a, b WHERE a.id = b.id
核心目标: 禁止用逗号分隔多表 + WHERE 条件关联，必须用显式 JOIN ... ON
正确写法: 显式 JOIN ... ON

违规: SELECT a.id FROM a, b WHERE a.id = b.id
正确: SELECT a.id FROM a JOIN b ON a.id = b.id
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation


class NoImplicitJoinChecker(BaseChecker):

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            # FROM 后面跟多个表（逗号连接）会被 SQLGlot 解析为 Join(kind="CROSS")
            for node in stmt.find_all(exp.Join):
                if node.kind == "CROSS" and node.args.get("on") is None and node.args.get("using") is None:
                    violations.append(Violation(
                                                message="禁止隐式 JOIN（FROM a, b），请改为显式 JOIN ... ON",
                    ))
        return violations
