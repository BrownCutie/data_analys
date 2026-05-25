from checker.base import CheckContext
from checker.hard.no_count_star import NoCountStarChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_count_star_violation():
    result = NoCountStarChecker().check(ctx("SELECT COUNT(*) FROM t"))
    assert len(result) == 1
    assert result[0].rule == "SQL-COUNT-001"


def test_count_one_pass():
    result = NoCountStarChecker().check(ctx("SELECT COUNT(1) FROM t"))
    assert result == []
