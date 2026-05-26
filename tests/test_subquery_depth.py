from checker.base import CheckContext
from checker.convention.subquery.subquery_depth import SubqueryDepthChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass_shallow():
    sql = "SELECT * FROM (SELECT * FROM t WHERE pt_d = '20260101') t0"
    violations = _check(sql, SubqueryDepthChecker)
    assert violations == []


def test_pass_max():
    sql = (
        "SELECT * FROM ("
        "SELECT * FROM ("
        "SELECT * FROM ("
        "SELECT * FROM t WHERE pt_d = '20260101'"
        ") t0"
        ") t1"
        ") t2"
    )
    violations = _check(sql, SubqueryDepthChecker)
    assert violations == []


def test_fail_deep():
    sql = (
        "SELECT * FROM ("
        "SELECT * FROM ("
        "SELECT * FROM ("
        "SELECT * FROM ("
        "SELECT * FROM t WHERE pt_d = '20260101'"
        ") t0"
        ") t1"
        ") t2"
        ") t3"
    )
    violations = _check(sql, SubqueryDepthChecker)
    assert len(violations) == 1
    assert violations[0].severity == "warning"
