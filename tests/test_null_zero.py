from checker.base import CheckContext
from checker.convention.null_zero import NullZeroChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_division_without_protection():
    result = NullZeroChecker().check(ctx("SELECT a.click_cnt / b.total_cnt FROM t"))
    assert len(result) >= 1


def test_division_with_coalesce_pass():
    result = NullZeroChecker().check(ctx("SELECT COALESCE(a.click_cnt / NULLIF(b.total_cnt, 0), 0) FROM t"))
    assert result == []
