from checker.base import CheckContext
from checker.no_distinct import NoDistinctChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_distinct_violation():
    result = NoDistinctChecker().check(ctx("SELECT DISTINCT user_id FROM t"))
    assert len(result) == 1
    assert result[0].rule == "SQL-DISTINCT-001"


def test_no_distinct_pass():
    result = NoDistinctChecker().check(ctx("SELECT user_id FROM t GROUP BY user_id"))
    assert result == []
