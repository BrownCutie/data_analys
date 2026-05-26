import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checker.runner import RuleRunner


runner = RuleRunner()


def test_compliant_sql():
    sql = """
    SELECT t0.user_id, COUNT(1) AS click_cnt
    FROM (
        SELECT a.user_id
        FROM dwd_xxx_click_di a
        WHERE a.pt_d BETWEEN '20260501' AND '20260507'
        GROUP BY a.user_id
    ) t0
    GROUP BY t0.user_id
    """
    result = runner.run(sql)
    assert result["passed"] is True
    assert result["violations"] == []


def test_multiple_violations():
    sql = "SELECT DISTINCT user_id FROM t"
    result = runner.run(sql)
    assert result["passed"] is False
    rules = [v["rule"] for v in result["violations"]]
    assert "SQL-DISTINCT-001" in rules
    assert "SQL-PARTITION-001" in rules


def test_parse_error():
    result = runner.run("SELECT SELECT FROM")
    assert result["passed"] is False
    assert "parse_error" in result
