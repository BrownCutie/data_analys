from __future__ import annotations

"""
规范检查 - 临时表命名规范

触发关键字: 临时表 (CREATE/INSERT 包含 tmp_)
核心目标: 临时表命名需符合公司规范，禁止随意命名
         推荐格式: tmp_{业务域}_{功能描述}_{日期后缀}
         例如: tmp_user_login_20260501

违规: CREATE TABLE tmp_abc AS SELECT ...
违规: INSERT INTO tmp_xxx ...
正确: CREATE TABLE tmp_user_login_20260501 AS SELECT ...
"""

import re

import sqlglot.expressions as exp

from checker.base import BaseChecker, CheckContext, Violation

TMP_NAME_PATTERN = re.compile(r"^tmp_[a-z][a-z0-9]*_[a-z][a-z0-9]*(?:_\d{8})?$")


class TempTableNamingChecker(BaseChecker):
    rule_id = "SQL-TEMP-TABLE-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, (exp.Create, exp.Insert)):
                    table = node.find(exp.Table)
                    if table is None:
                        continue
                    name = table.name
                    if not name.startswith("tmp_"):
                        continue
                    if not TMP_NAME_PATTERN.match(name):
                        violations.append(
                            Violation(
                                message=f"临时表 '{name}' 命名不规范，推荐格式: tmp_{{业务域}}_{{描述}}_{{日期}}",
                                severity="warning",
                            )
                        )
        return violations
