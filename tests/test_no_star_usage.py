import sqlglot

from checker.base import CheckContext
from checker.hard.select.no_star_usage import NoStarUsageChecker

_checker = NoStarUsageChecker()


def _check(sql: str):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return _checker.check(ctx)


def test_pass():
    violations = _check("SELECT t.user_id FROM t WHERE pt_d = '20260101'")
    assert len(violations) == 0


def test_fail_select_star():
    violations = _check("SELECT * FROM t")
    assert len(violations) == 1
    assert "SELECT *" in violations[0].message


def test_fail_count_star():
    violations = _check("SELECT COUNT(*) FROM t")
    assert len(violations) == 1
    assert "聚合" in violations[0].message


def test_fail_table_star():
    violations = _check("SELECT t.* FROM t")
    assert len(violations) == 1
    assert "*" in violations[0].message
