from checker.base import CheckContext
from checker.convention.join.join_filter_first import JoinFilterFirstChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "SELECT a.id FROM (SELECT * FROM t1 WHERE pt_d = '20260101') a JOIN t2 b ON a.id = b.id"
    violations = _check(sql, JoinFilterFirstChecker)
    assert violations == []


def test_fail():
    sql = "SELECT a.id FROM t1 a JOIN t2 b ON a.id = b.id WHERE a.pt_d = '20260101'"
    violations = _check(sql, JoinFilterFirstChecker)
    assert len(violations) == 1
    assert violations[0].severity == "warning"
