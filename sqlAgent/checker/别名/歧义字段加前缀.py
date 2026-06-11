from __future__ import annotations

"""
规范检查 - 歧义字段必须带表别名前缀

触发关键字: 多表, JOIN, 子查询
核心目标: 仅当字段名同时出现在多个表中时，引用该字段必须带表别名前缀；
         若字段只存在于某一个表，可省略前缀
正确写法: SELECT t0.user_id, amount FROM t0 JOIN t1 ON t0.user_id = t1.user_id

违规: SELECT user_id FROM t0 JOIN t1 ON t0.user_id = t1.user_id
正确: SELECT t0.user_id FROM t0 JOIN t1 ON t0.user_id = t1.user_id
合规: SELECT amount FROM t0 JOIN t1 ON t0.id = t1.id  -- amount 仅属单表，可不加前缀
"""

from collections import defaultdict

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation


class AmbiguousColumnPrefixChecker(BaseChecker):
    rule_id = "SQL-TABLE-ALIAS-001"
    name = "歧义字段加前缀"
    desc = "检查多表查询中同时出现在多个表的同名字段是否带表别名前缀。仅对可能产生歧义的字段要求加前缀，单表独有字段可省略。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        non_prefixed: set[str] = set()
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                if not self._is_multi_table(select):
                    continue
                ambiguous = self._ambiguous_columns(select)
                for col in self._scope_columns(select):
                    if not col.table and col.name in ambiguous:
                        non_prefixed.add(col.name)

        if not non_prefixed:
            return []

        field_list = ", ".join(sorted(non_prefixed))
        return [
            Violation(
                message=(
                    f"以下字段同时出现在多个表中且未带表别名前缀: {field_list}，"
                    "请添加表别名前缀以消除歧义。"
                ),
            )
        ]

    @staticmethod
    def _is_multi_table(select: exp.Select) -> bool:
        """Check if a SELECT involves multiple tables (JOINs or subqueries)."""
        if list(select.find_all(exp.Join)):
            return True
        from_clause = select.find(exp.From)
        if not from_clause:
            return False
        if list(from_clause.find_all(exp.Subquery)):
            return True
        return len(list(from_clause.find_all(exp.Table))) > 1

    def _ambiguous_columns(self, select: exp.Select) -> set[str]:
        """Infer column names that appear in more than one table within this SELECT."""
        table_map: dict[str, set[str]] = defaultdict(set)
        for node in self._walk_scope(select):
            if isinstance(node, exp.Column) and node.table and node.name:
                table_map[node.name].add(node.table)
            elif isinstance(node, exp.EQ):
                left, right = node.this, node.expression
                if (
                    isinstance(left, exp.Column)
                    and isinstance(right, exp.Column)
                    and left.name
                    and left.name == right.name
                    and left.table
                    and right.table
                    and left.table != right.table
                ):
                    table_map[left.name].add(left.table)
                    table_map[left.name].add(right.table)
        return {name for name, tables in table_map.items() if len(tables) > 1}

    def _scope_columns(self, select: exp.Select) -> list[exp.Column]:
        return [node for node in self._walk_scope(select) if isinstance(node, exp.Column)]

    def _walk_scope(self, node: exp.Expression):
        """Traverse nodes in the current SELECT scope, skipping nested subqueries."""
        if isinstance(node, exp.Subquery):
            return
        yield node
        for child in node.iter_expressions():
            if isinstance(child, exp.Subquery):
                continue
            yield from self._walk_scope(child)
