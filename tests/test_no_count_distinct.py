from checker.base import CheckContext
from checker.hard.no_count_distinct import NoCountDistinctChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_count_distinct_violation():
    result = NoCountDistinctChecker().check(ctx("SELECT COUNT(DISTINCT user_id) FROM t"))
    assert len(result) == 1


def test_count_distinct_pass():
    result = NoCountDistinctChecker().check(ctx("SELECT COUNT(1) FROM (SELECT user_id FROM t GROUP BY user_id) t0"))
    assert result == []
