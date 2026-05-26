from __future__ import annotations

from checker.base import CheckContext
from checker.hard.cte.no_cte import NoCteChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass():
    violations = _check(
        "SELECT user_id FROM t WHERE pt_d = '20260101'",
        NoCteChecker,
    )
    assert violations == []


def test_fail():
    violations = _check(
        "WITH t0 AS (SELECT user_id FROM user_table) SELECT * FROM t0",
        NoCteChecker,
    )
    assert len(violations) == 1
