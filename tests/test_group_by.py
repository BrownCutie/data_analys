from checker.base import CheckContext
from checker.convention.aggregate.group_by import GroupByChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "SELECT user_id, city, COUNT(1) AS cnt FROM t GROUP BY user_id, city"
    violations = _check(sql, GroupByChecker)
    assert violations == []


def test_fail():
    sql = "SELECT user_id, city, COUNT(1) AS cnt FROM t GROUP BY user_id"
    violations = _check(sql, GroupByChecker)
    assert len(violations) >= 1
    messages = " ".join(v.message for v in violations)
    assert "city" in messages
