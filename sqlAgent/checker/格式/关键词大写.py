from __future__ import annotations

"""
规范检查 - SQL 关键词必须大写

触发关键字: SQL 关键词 (SELECT, FROM, WHERE, JOIN 等)
核心目标: 所有关键词必须使用大写，提高可读性
正确写法: SELECT user_id FROM t WHERE pt_d = '20260101'

违规: select user_id from t where pt_d = '20260101'
正确: SELECT user_id FROM t WHERE pt_d = '20260101'
"""

import re

from checker.base import BaseChecker, CheckContext, Violation

KEYWORDS = (
    "select",
    "from",
    "where",
    "join",
    "left",
    "right",
    "inner",
    "outer",
    "cross",
    "on",
    "and",
    "or",
    "not",
    "in",
    "is",
    "null",
    "as",
    "group",
    "by",
    "order",
    "having",
    "distinct",
    "union",
    "all",
    "case",
    "when",
    "then",
    "else",
    "end",
    "between",
    "like",
    "exists",
    "insert",
    "into",
    "values",
    "create",
    "table",
    "drop",
    "alter",
    "update",
    "delete",
    "set",
    "count",
    "sum",
    "avg",
    "min",
    "max",
    "coalesce",
    "nvl",
    "nullif",
    "cast",
    "with",
    "limit",
    "desc",
    "asc",
    "over",
    "partition",
)

_KEYWORDS_PATTERN = re.compile(
    r"\b(" + "|".join(KEYWORDS) + r")\b", re.IGNORECASE
)

_STRING_LITERAL_PATTERN = re.compile(r"'(?:[^'\\]|\\.)*'")


class KeywordUppercaseChecker(BaseChecker):
    rule_id = "SQL-KEYWORD-CASE-001"
    name = "关键词大写规范"
    desc = "检查 SQL 保留关键词（SELECT、FROM、WHERE 等）是否使用大写。统一大写便于快速阅读和团队风格一致。"

    def check(self, ctx: CheckContext) -> list[Violation]:
        # Replace string literals with placeholders to avoid false positives
        sanitized = _STRING_LITERAL_PATTERN.sub("''", ctx.raw_sql)

        non_compliant: set[str] = set()
        for match in _KEYWORDS_PATTERN.finditer(sanitized):
            matched_text = match.group(1)
            if matched_text != matched_text.upper():
                non_compliant.add(matched_text.lower())

        if not non_compliant:
            return []

        keyword_list = ", ".join(sorted(non_compliant))
        return [
            Violation(
                message=f"以下关键词未使用大写: {keyword_list}，请全部改为大写。",
            )
        ]