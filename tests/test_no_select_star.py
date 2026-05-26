from checker.base import CheckContext
from checker.hard.no_select_star import NoSelectStarChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_select_star_violation():
    result = NoSelectStarChecker().check(ctx("SELECT * FROM t"))
    assert len(result) == 1


def test_explicit_fields_pass():
    result = NoSelectStarChecker().check(ctx("SELECT user_id, order_id FROM t"))
    assert result == []
