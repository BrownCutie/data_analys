import sqlglot

from checker.base import CheckContext
from checker.hard.join.no_cross_join import NoCrossJoinChecker

_checker = NoCrossJoinChecker()


def _check(sql: str):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return _checker.check(ctx)


def test_pass():
    violations = _check(
        "SELECT a.id FROM t1 a INNER JOIN t2 b ON a.id = b.id WHERE a.pt_d = '20260101'"
    )
    assert len(violations) == 0


def test_fail():
    violations = _check("SELECT a.id FROM t1 a CROSS JOIN t2 b")
    assert len(violations) == 1
    assert "CROSS JOIN" in violations[0].message
