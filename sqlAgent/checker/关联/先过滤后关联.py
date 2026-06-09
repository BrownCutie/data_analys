"""
先过滤后关联

触发关键字: JOIN, WHERE, pt_d, pt_h, pt_m, pt_w
核心目标: 分区过滤条件必须下推到 JOIN 前的子查询中，不能在外层 JOIN 后才过滤
违规示例:
    SELECT * FROM orders o JOIN users u ON o.user_id = u.id WHERE o.pt_d = '2024-01-01'
正确写法:
    SELECT * FROM (SELECT * FROM orders WHERE pt_d = '2024-01-01') o
    JOIN users u ON o.user_id = u.id
"""

from __future__ import annotations

from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation

PARTITION_FIELDS = {"pt_d", "pt_h", "pt_m", "pt_w"}


class FilterBeforeJoinChecker(BaseChecker):
    rule_id = "SQL-JOIN-FILTER-001"
    name = "先过滤后关联"
    desc = "分区过滤条件必须下推到 JOIN 前的子查询中，不能在外层 JOIN 后才过滤"

    def _has_partition_condition(self, where_clause: exp.Expression) -> bool:
        """检查 WHERE 子句中是否包含分区字段"""
        for col in where_clause.find_all(exp.Column):
            if col.name in PARTITION_FIELDS:
                return True
        return False

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for statement in ctx.statements:
            for select in statement.find_all(exp.Select):
                # 只检查当前 SELECT 直接的 WHERE 子句，不递归进入子查询
                where_clause = select.args.get("where")
                if not where_clause:
                    continue

                # 检查当前 SELECT 是否有 JOIN
                joins = list(select.find_all(exp.Join))
                if not joins:
                    continue

                # 检查外层 WHERE 是否包含分区过滤条件
                if self._has_partition_condition(where_clause):
                    violations.append(
                        Violation(
                            message="分区过滤条件未下推，建议将分区过滤移到 JOIN 前的子查询中"
                        )
                    )
        return violations
