from fastmcp import FastMCP

from checker.runner import RuleRunner

mcp = FastMCP("spark-sql-quality-mcp")

runner = RuleRunner()


@mcp.tool
def check_sql_compliance(sql: str) -> dict:
    """检查 Spark SQL 是否符合公司内部 SQL 书写规范。

    在生成或修改 SQL 后调用，返回违规报告（含 rule、message、severity）。
    Agent 不需要选择具体规则，所有启用的规则会自动执行。

    返回格式：{"passed": bool, "violations": [{"rule": str, "message": str, "severity": str}]}
    severity 取值：error（硬性违规，必须修复）/ warning（规范检查，必须符合约定）
    """
    return runner.run(sql)
