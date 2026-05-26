import sqlglot

from checker.base import CheckContext
from checker.hard.aggregate.no_distinct import NoDistinctChecker

_checker = NoDistinctChecker()


def _check(sql: str):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return _checker.check(ctx)


def test_pass():
    violations = _check("SELECT user_id FROM t GROUP BY user_id")
    assert len(violations) == 0


def test_fail_select_distinct():
    violations = _check("SELECT DISTINCT user_id FROM t")
    assert len(violations) == 1
    assert "DISTINCT" in violations[0].message


def test_fail_count_distinct():
    violations = _check("SELECT COUNT(DISTINCT user_id) FROM t")
    assert len(violations) == 1
    assert "DISTINCT" in violations[0].message
