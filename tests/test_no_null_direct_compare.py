from __future__ import annotations

from checker.base import CheckContext
from checker.hard.null.no_null_direct_compare import NullDirectCompareChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass_is_null():
    violations = _check(
        "SELECT * FROM t WHERE a IS NULL AND pt_d = '20260101'",
        NullDirectCompareChecker,
    )
    assert violations == []


def test_pass_is_not_null():
    violations = _check(
        "SELECT * FROM t WHERE a IS NOT NULL AND pt_d = '20260101'",
        NullDirectCompareChecker,
    )
    assert violations == []


def test_pass_nvl():
    violations = _check(
        "SELECT * FROM t WHERE NVL(a, '') != '' AND pt_d = '20260101'",
        NullDirectCompareChecker,
    )
    assert violations == []


def test_fail_eq_null():
    violations = _check(
        "SELECT * FROM t WHERE a = NULL",
        NullDirectCompareChecker,
    )
    assert len(violations) == 1


def test_fail_neq_null():
    violations = _check(
        "SELECT * FROM t WHERE a != NULL",
        NullDirectCompareChecker,
    )
    assert len(violations) == 1


def test_fail_gt_null():
    violations = _check(
        "SELECT * FROM t WHERE a > NULL",
        NullDirectCompareChecker,
    )
    assert len(violations) == 1
