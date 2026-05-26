from __future__ import annotations

from checker.base import CheckContext
from checker.hard.null.null_zero import NullZeroChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    violations = _check(
        "SELECT COALESCE(a / NULLIF(b, 0), 0) FROM t WHERE pt_d = '20260101'",
        NullZeroChecker,
    )
    assert violations == []


def test_fail_no_protection():
    violations = _check(
        "SELECT a / b FROM t WHERE pt_d = '20260101'",
        NullZeroChecker,
    )
    assert len(violations) == 1


def test_fail_only_nullif():
    violations = _check(
        "SELECT a / NULLIF(b, 0) FROM t WHERE pt_d = '20260101'",
        NullZeroChecker,
    )
    assert len(violations) == 1
