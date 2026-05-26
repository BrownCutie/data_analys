from __future__ import annotations

from checker.base import CheckContext
from checker.hard.partition.partition_required import PartitionRequiredChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass_pt_d():
    violations = _check(
        "SELECT user_id FROM t WHERE pt_d = '20260101'",
        PartitionRequiredChecker,
    )
    assert violations == []


def test_pass_pt_h():
    violations = _check(
        "SELECT user_id FROM t WHERE pt_h = '03'",
        PartitionRequiredChecker,
    )
    assert violations == []


def test_pass_pt_m():
    violations = _check(
        "SELECT user_id FROM t WHERE pt_m = '202603'",
        PartitionRequiredChecker,
    )
    assert violations == []


def test_pass_pt_w():
    violations = _check(
        "SELECT user_id FROM t WHERE pt_w = '20250603'",
        PartitionRequiredChecker,
    )
    assert violations == []


def test_fail_no_partition():
    violations = _check(
        "SELECT user_id FROM t WHERE status = 1",
        PartitionRequiredChecker,
    )
    assert len(violations) == 1
