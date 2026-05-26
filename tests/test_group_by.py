from checker.base import CheckContext
from checker.convention.group_by import GroupByChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_missing_group_by_col():
    result = GroupByChecker().check(ctx("SELECT user_id, city, COUNT(1) FROM t GROUP BY user_id"))
    assert len(result) >= 1


def test_complete_group_by_pass():
    result = GroupByChecker().check(ctx("SELECT user_id, city, COUNT(1) AS cnt FROM t GROUP BY user_id, city"))
    assert result == []
