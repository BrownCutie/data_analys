"""
硬性规则 - 聚合/计算字段必须有清晰别名

触发关键字: 聚合函数, CASE WHEN, 算术表达式
核心目标: 聚合函数、CASE WHEN、算术表达式必须有清晰的 AS 别名
         禁止无意义别名如 cnt, num1, aaa, col1, tmp 等
正确写法: COUNT(1) AS click_cnt, CASE WHEN ... END AS is_new_user

违规: SELECT COUNT(1) FROM t
违规: SELECT COUNT(1) AS cnt FROM t
正确: SELECT COUNT(1) AS click_cnt FROM t
"""

from __future__ import annotations

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

BAD_ALIASES = frozenset(
    {"cnt", "num", "num1", "aaa", "col", "col1", "tmp", "temp", "a", "b", "c", "x", "y", "z"}
)

_AGGREGATE_TYPES = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max)
_COMPUTED_TYPES = (exp.Case, exp.If)


def _needs_alias(node: exp.Expression) -> bool:
    """Return True if the expression is an aggregate or computed field that requires an alias."""
    if isinstance(node, _AGGREGATE_TYPES):
        return True
    if isinstance(node, _COMPUTED_TYPES):
        return True
    # Arithmetic expressions (binary ops like Add, Sub, Mul, Div)
    if isinstance(node, (exp.Add, exp.Sub, exp.Mul, exp.Div, exp.Mod)):
        return True
    return False


def _contains_aggregate_or_computed(node: exp.Expression) -> bool:
    """Return True if node itself or any child matches aggregate/computed types."""
    if _needs_alias(node):
        return True
    for child in node.iter_expressions():
        if _contains_aggregate_or_computed(child):
            return True
    return False


class FieldAliasChecker(BaseChecker):
    rule_id = "SQL-FIELD-ALIAS-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                for expr in select.expressions:
                    if not _contains_aggregate_or_computed(expr):
                        continue
                    alias = expr.args.get("alias")
                    if alias is None:
                        violations.append(
                            Violation(
                                message="聚合/计算字段必须有 AS 别名",
                                severity="warning",
                            )
                        )
                    else:
                        alias_name = alias if isinstance(alias, str) else alias.name
                        if alias_name.lower() in BAD_ALIASES:
                            violations.append(
                                Violation(
                                    message=f"别名 '{alias_name}' 无意义，请使用能表达业务含义的名称",
                                    severity="warning",
                                )
                            )
        return violations
