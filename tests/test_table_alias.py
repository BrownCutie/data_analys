from checker.base import CheckContext
from checker.convention.alias.table_alias import TableAliasChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    sql = "SELECT a.user_id FROM t1 a LEFT JOIN t2 b ON a.id = b.id"
    violations = _check(sql, TableAliasChecker)
    assert violations == []


def test_pass_single_table():
    sql = "SELECT user_id FROM t"
    violations = _check(sql, TableAliasChecker)
    assert violations == []


def test_fail_unqualified():
    sql = "SELECT user_id FROM t1 a LEFT JOIN t2 b ON a.id = b.id"
    violations = _check(sql, TableAliasChecker)
    assert len(violations) == 1
    assert "user_id" in violations[0].message
