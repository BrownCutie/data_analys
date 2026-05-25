from checker.base import CheckContext
from checker.field_alias import FieldAliasChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_field_no_alias_violation():
    result = FieldAliasChecker().check(ctx("SELECT user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id"))
    assert len(result) >= 1
    assert result[0].rule == "SQL-FIELD-ALIAS-001"
    assert result[0].severity == "warning"


def test_field_with_alias_pass():
    result = FieldAliasChecker().check(ctx("SELECT t0.user_id FROM t0 LEFT JOIN t1 ON t0.id = t1.id"))
    assert result == []


def test_single_table_pass():
    result = FieldAliasChecker().check(ctx("SELECT user_id FROM t"))
    assert result == []
