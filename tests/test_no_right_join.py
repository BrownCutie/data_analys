from checker.base import CheckContext
from checker.hard.no_right_join import NoRightJoinChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_right_join_violation():
    result = NoRightJoinChecker().check(ctx("SELECT a.id FROM a RIGHT JOIN b ON a.id = b.id"))
    assert len(result) == 1
    assert result[0].rule == "SQL-JOIN-RIGHT-001"


def test_left_join_pass():
    result = NoRightJoinChecker().check(ctx("SELECT a.id FROM a LEFT JOIN b ON a.id = b.id"))
    assert result == []
