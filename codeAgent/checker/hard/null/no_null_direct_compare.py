from __future__ import annotations

"""
硬性规则 - 禁止 NULL 直接判断

触发关键字: = NULL, != NULL, > NULL, < NULL
核心目标: 禁止对 NULL 使用直接比较运算符，必须使用 IS NULL / IS NOT NULL
         或使用 NVL() / COALESCE() 等函数处理
正确写法: a IS NULL, a IS NOT NULL, NVL(a, '') != ''

违规: SELECT * FROM t WHERE a = NULL
违规: SELECT * FROM t WHERE a != NULL
违规: SELECT * FROM t WHERE a > NULL
正确: SELECT * FROM t WHERE a IS NULL
正确: SELECT * FROM t WHERE a IS NOT NULL
正确: SELECT * FROM t WHERE NVL(a, '') != ''
"""

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

# 直接比较运算符（不含 IS / IS NOT）
_COMPARE_TYPES = (exp.EQ, exp.NEQ, exp.GT, exp.LT, exp.GTE, exp.LTE, exp.Like)


class NullDirectCompareChecker(BaseChecker):
    rule_id = "SQL-NULL-COMPARE-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if not isinstance(node, _COMPARE_TYPES):
                    continue
                # node.this  → 左侧,  node.expression → 右侧
                if isinstance(node.this, exp.Null) or isinstance(
                    node.expression, exp.Null
                ):
                    violations.append(
                        Violation(
                            message="禁止对 NULL 使用直接比较运算符（=、!=、>、<），"
                            "请使用 IS NULL / IS NOT NULL / NVL() / COALESCE()"
                        )
                    )
        return violations
