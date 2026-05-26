from checker.base import CheckContext
from checker.convention.format.keyword_uppercase import KeywordUppercaseChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "SELECT user_id FROM t WHERE pt_d = '20260101'"
    violations = _check(sql, KeywordUppercaseChecker)
    assert violations == []


def test_fail():
    sql = "select user_id from t where pt_d = '20260101'"
    violations = _check(sql, KeywordUppercaseChecker)
    assert len(violations) >= 1
    # Check that the violations mention lowercase keywords
    messages = " ".join(v.message for v in violations)
    assert "select" in messages.lower() or "大写" in messages
