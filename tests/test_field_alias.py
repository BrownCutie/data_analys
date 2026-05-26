from checker.base import CheckContext
from checker.convention.field_alias import FieldAliasChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_no_alias_violation():
    result = FieldAliasChecker().check(ctx("SELECT COUNT(1) FROM t"))
    assert len(result) == 1


def test_bad_alias_violation():
    result = FieldAliasChecker().check(ctx("SELECT COUNT(1) AS cnt FROM t"))
    assert len(result) == 1
    assert "无意义" in result[0].message


def test_good_alias_pass():
    result = FieldAliasChecker().check(ctx("SELECT COUNT(1) AS click_cnt FROM t"))
    assert result == []
