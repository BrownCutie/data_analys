from checker.base import CheckContext
from checker.convention.sort.order_by_limit import OrderByLimitChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "SELECT user_id FROM t WHERE pt_d = '20260101' ORDER BY user_id LIMIT 100"
    violations = _check(sql, OrderByLimitChecker)
    assert violations == []


def test_fail():
    sql = "SELECT user_id FROM t WHERE pt_d = '20260101' ORDER BY user_id"
    violations = _check(sql, OrderByLimitChecker)
    assert len(violations) == 1
    assert "LIMIT" in violations[0].message
