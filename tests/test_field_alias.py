import sqlglot

from checker.base import CheckContext
from checker.hard.aggregate.field_alias import FieldAliasChecker

_checker = FieldAliasChecker()


def _check(sql: str):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return _checker.check(ctx)


def test_pass():
    violations = _check("SELECT COUNT(1) AS click_cnt FROM t WHERE pt_d = '20260101'")
    assert len(violations) == 0


def test_pass_plain_column():
    violations = _check("SELECT user_id FROM t WHERE pt_d = '20260101'")
    assert len(violations) == 0


def test_fail_no_alias():
    violations = _check("SELECT COUNT(1) FROM t WHERE pt_d = '20260101'")
    assert len(violations) == 1
    assert "别名" in violations[0].message


def test_fail_bad_alias():
    violations = _check("SELECT COUNT(1) AS cnt FROM t WHERE pt_d = '20260101'")
    assert len(violations) == 1
    assert "无意义" in violations[0].message
