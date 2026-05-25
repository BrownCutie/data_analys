from fastmcp import FastMCP

from checker.runner import RuleRunner

mcp = FastMCP("spark-sql-quality-mcp")

runner = RuleRunner()


@mcp.tool
def check_sql_compliance(sql: str) -> dict:
    """检查 Spark SQL 是否符合公司内部 SQL 书写规范。

    该工具使用 SQLGlot 按 Spark 方言解析 SQL，并按 MCP 内部配置依次执行所有启用的规则。
    Agent 不需要、也不能选择具体规则；只需在生成或修改 SQL 后调用本工具进行统一检查。
    """
    return runner.run(sql)
