from checker.base import CheckContext
from checker.convention.subquery_alias import SubqueryAliasChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_subquery_no_alias_violation():
    result = SubqueryAliasChecker().check(ctx("SELECT * FROM (SELECT user_id FROM t)"))
    assert len(result) == 1
    assert result[0].rule == "SQL-SUBQUERY-ALIAS-001"


def test_subquery_with_alias_pass():
    result = SubqueryAliasChecker().check(ctx("SELECT * FROM (SELECT user_id FROM t) t0"))
    assert result == []
