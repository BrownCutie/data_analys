"""
规范检查 - 计算字段/聚合字段必须有清晰别名

触发关键字: 字段别名 (计算, 聚合, CASE WHEN)
核心目标: 聚合函数、CASE WHEN、算术表达式必须有清晰的 AS 别名
         禁止无意义别名如 cnt, num1, aaa, col1, tmp 等
正确写法: COUNT(1) AS click_cnt, CASE WHEN ... END AS is_new_user

违规: SELECT COUNT(1) FROM t
违规: SELECT COUNT(1) AS cnt FROM t
正确: SELECT COUNT(1) AS click_cnt FROM t
"""

from __future__ import annotations

from sqlglot import exp

from ..base import BaseChecker, CheckContext, Violation

# 禁止使用的无意义别名
BAD_ALIASES = {"cnt", "num", "num1", "aaa", "col", "col1", "tmp", "temp", "a", "b", "c", "x", "y", "z"}

# 需要强制有别名的表达式类型
ALIAS_REQUIRED_TYPES = (exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max, exp.Case, exp.If)


class FieldAliasChecker(BaseChecker):

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            if not isinstance(stmt, exp.Select):
                continue
            for expression in stmt.expressions:
                # 检查是否是聚合/计算表达式
                has_agg_or_calc = any(isinstance(expression, t) for t in ALIAS_REQUIRED_TYPES)
                # 也检查表达式内部是否嵌套了聚合函数
                if not has_agg_or_calc:
                    for node in expression.walk():
                        if isinstance(node, ALIAS_REQUIRED_TYPES):
                            has_agg_or_calc = True
                            break
                if not has_agg_or_calc:
                    continue

                alias = expression.alias
                # 没有别名
                if not alias:
                    violations.append(Violation(
                                                message="聚合/计算字段必须有 AS 别名",
                        severity="warning",
                    ))
                # 别名无意义
                elif alias.lower() in BAD_ALIASES:
                    violations.append(Violation(
                                                message=f"别名 '{alias}' 无意义，请使用能表达业务含义的名称",
                        severity="warning",
                    ))
        return violations
