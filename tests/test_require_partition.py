from checker.base import CheckContext
from checker.convention.partition_filter import PartitionFilterChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_no_partition_violation():
    result = PartitionFilterChecker().check(ctx("SELECT user_id FROM t"))
    assert len(result) == 1
    assert result[0].rule == "SQL-PARTITION-001"


def test_partition_ptd_pass():
    result = PartitionFilterChecker().check(ctx("SELECT user_id FROM t WHERE pt_d = '20260101'"))
    assert result == []


def test_partition_pth_pass():
    result = PartitionFilterChecker().check(ctx("SELECT user_id FROM t WHERE pt_h = '12'"))
    assert result == []
