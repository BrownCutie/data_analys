from checker.base import CheckContext
from checker.convention.naming.temp_table_naming import TempTableNamingChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "CREATE TABLE tmp_user_login_20260501 AS SELECT * FROM t"
    violations = _check(sql, TempTableNamingChecker)
    assert violations == []


def test_fail():
    sql = "CREATE TABLE tmp_abc AS SELECT * FROM t"
    violations = _check(sql, TempTableNamingChecker)
    assert len(violations) == 1
    assert "tmp_abc" in violations[0].message
