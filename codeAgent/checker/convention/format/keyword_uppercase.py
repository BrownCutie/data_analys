"""
规范检查 - SQL 关键词必须大写

触发关键字: SQL 关键词 (SELECT, FROM, WHERE, JOIN 等)
核心目标: 所有关键词必须使用大写，提高可读性
正确写法: SELECT user_id FROM t WHERE pt_d = '20260101'

违规: select user_id from t where pt_d = '20260101'
正确: SELECT user_id FROM t WHERE pt_d = '20260101'
"""

from __future__ import annotations

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

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations: list[Violation] = []
        # Replace string literals with placeholders to avoid false positives
        sanitized = _STRING_LITERAL_PATTERN.sub("''", ctx.raw_sql)

        seen: set[str] = set()
        for match in _KEYWORDS_PATTERN.finditer(sanitized):
            matched_text = match.group(1)
            if matched_text != matched_text.upper() and matched_text.lower() not in seen:
                seen.add(matched_text.lower())
                violations.append(
                    Violation(
                        message=f"SQL 关键词 '{matched_text}' 应使用大写，请改为 '{matched_text.upper()}'",
                        severity="warning",
                    )
                )
        return violations
