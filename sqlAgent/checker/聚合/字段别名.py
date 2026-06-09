"""
聚合字段别名

触发关键字: SELECT, AS, COUNT, SUM, AVG, CASE WHEN
核心目标: 聚合函数、CASE WHEN、算术表达式必须有清晰的 AS 别名
违规示例:
    SELECT COUNT(*) FROM orders
    SELECT COUNT(*) cnt FROM orders
    SELECT SUM(amount) aaa FROM orders
正确写法:
    SELECT COUNT(*) AS order_count FROM orders
    SELECT SUM(amount) AS total_amount FROM orders
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

BAD_ALIASES = {
    "cnt", "num", "num1", "aaa", "col", "col1",
    "tmp", "temp", "a", "b", "c", "x", "y", "z",
}

ALIAS_REQUIRED_TYPES = (
    exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max,
    exp.Case, exp.If,
)


class FieldAliasChecker(BaseChecker):
    rule_id = "SQL-FIELD-ALIAS-001"
    name = "聚合字段别名"
    desc = "聚合函数、CASE WHEN、算术表达式必须有清晰的 AS 别名，禁用 cnt/num/tmp 等无意义别名"

    def _needs_alias(self, node: exp.Expression) -> bool:
        """判断表达式是否是聚合/CASE/IF 类型，需要别名"""
        if isinstance(node, ALIAS_REQUIRED_TYPES):
            return True
        # Div、Mul、Add、Sub 等算术运算也需要别名
        if isinstance(node, (exp.Div, exp.Mul, exp.Add, exp.Sub)):
            return True
        return False

    def _is_alias_required_expr(self, node: exp.Expression) -> bool:
        """判断 SELECT 表达式是否包含需要别名的子表达式"""
        # 直接就是聚合/CASE/IF
        if self._needs_alias(node):
            return True
        # 包含聚合/CASE/IF 子表达式
        for child in node.find_all(*ALIAS_REQUIRED_TYPES):
            return True
        return False

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for select in statement.find_all(exp.Select):
                for expr in select.expressions:
                    # 跳过 * 的情况
                    if isinstance(expr, exp.Star):
                        continue
                    # 获取实际表达式和别名
                    actual_expr = expr
                    alias_node = expr.alias
                    if isinstance(expr, exp.Alias):
                        actual_expr = expr.this
                        alias_name = alias_node if isinstance(alias_node, str) else str(alias_node)
                    else:
                        alias_name = None

                    if not self._is_alias_required_expr(actual_expr):
                        continue

                    if alias_name is None:
                        violations.append(
                            Violation(message="聚合/计算字段必须有 AS 别名")
                        )
                    elif alias_name.lower() in BAD_ALIASES:
                        violations.append(
                            Violation(
                                message=f"别名 '{alias_name}' 无意义，请使用能表达业务含义的名称"
                            )
                        )
        return violations
