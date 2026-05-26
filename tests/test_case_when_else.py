from checker.base import CheckContext
from checker.convention.format.case_when_else import CaseWhenElseChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "SELECT CASE WHEN x > 0 THEN 'yes' ELSE 'no' END AS flag FROM t"
    violations = _check(sql, CaseWhenElseChecker)
    assert violations == []


def test_fail():
    sql = "SELECT CASE WHEN x > 0 THEN 'yes' END AS flag FROM t"
    violations = _check(sql, CaseWhenElseChecker)
    assert len(violations) == 1
    assert "ELSE" in violations[0].message
