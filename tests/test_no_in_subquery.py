from __future__ import annotations

from checker.base import CheckContext
from checker.hard.subquery.no_in_subquery import NoInSubqueryChecker

import sqlglot


def _check(sql: str, checker_cls):
    statements = sqlglot.parse(sql, read="spark")
    ctx = CheckContext(raw_sql=sql, statements=[s for s in statements if s is not None])
    return checker_cls().check(ctx)


def test_pass_literal_list():
    violations = _check(
        "SELECT * FROM t WHERE id IN (1, 2, 3) AND pt_d = '20260101'",
        NoInSubqueryChecker,
    )
    assert violations == []


def test_fail():
    violations = _check(
        "SELECT * FROM t WHERE id IN (SELECT id FROM t2)",
        NoInSubqueryChecker,
    )
    assert len(violations) == 1
