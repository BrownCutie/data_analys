from checker.base import CheckContext
from checker.hard.no_implicit_join import NoImplicitJoinChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_implicit_join_violation():
    result = NoImplicitJoinChecker().check(ctx("SELECT a.id FROM a, b WHERE a.id = b.id"))
    assert len(result) == 1


def test_explicit_join_pass():
    result = NoImplicitJoinChecker().check(ctx("SELECT a.id FROM a JOIN b ON a.id = b.id"))
    assert result == []
