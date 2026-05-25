from checker.base import CheckContext
from checker.convention.temp_table_naming import TempTableNamingChecker
import sqlglot


def ctx(sql: str) -> CheckContext:
    return CheckContext(raw_sql=sql, statements=sqlglot.parse(sql, read="spark"))


def test_bad_temp_table_name():
    result = TempTableNamingChecker().check(ctx("CREATE TABLE tmp_abc AS SELECT 1"))
    assert len(result) == 1
    assert result[0].rule == "SQL-TEMP-TABLE-001"


def test_good_temp_table_name():
    result = TempTableNamingChecker().check(ctx("CREATE TABLE tmp_user_login_20260501 AS SELECT 1"))
    assert result == []
