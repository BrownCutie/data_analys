from checker.base import CheckContext
from checker.convention.join_filter_first import JoinFilterFirstChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_filter_not_pushed():
    sql = "SELECT a.id FROM big_table a JOIN detail_table b ON a.id = b.id WHERE a.pt_d = '20260101'"
    result = JoinFilterFirstChecker().check(ctx(sql))
    assert len(result) == 1


def test_no_join_pass():
    result = JoinFilterFirstChecker().check(ctx("SELECT id FROM t WHERE pt_d = '20260101'"))
    assert result == []
