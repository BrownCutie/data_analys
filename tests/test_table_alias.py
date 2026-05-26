from checker.base import CheckContext
from checker.convention.table_alias import TableAliasChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_field_no_alias_violation():
    result = TableAliasChecker().check(ctx("SELECT user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id"))
    assert len(result) >= 1


def test_field_with_alias_pass():
    result = TableAliasChecker().check(ctx("SELECT t0.user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id"))
    assert result == []


def test_single_table_pass():
    result = TableAliasChecker().check(ctx("SELECT user_id FROM t"))
    assert result == []
