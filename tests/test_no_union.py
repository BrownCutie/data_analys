from __future__ import annotations

from checker.base import CheckContext
from checker.hard.union.no_union import NoUnionChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass_union_all():
    violations = _check(
        "SELECT id FROM t1 WHERE pt_d = '20260101' UNION ALL SELECT id FROM t2 WHERE pt_d = '20260101'",
        NoUnionChecker,
    )
    assert violations == []


def test_fail_union():
    violations = _check(
        "SELECT id FROM t1 WHERE pt_d = '20260101' UNION SELECT id FROM t2 WHERE pt_d = '20260101'",
        NoUnionChecker,
    )
    assert len(violations) == 1
