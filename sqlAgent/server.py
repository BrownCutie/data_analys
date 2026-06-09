from fastmcp import FastMCP

from checker.registry import RULE_REGISTRY
from checker.runner import RuleRunner

mcp = FastMCP("spark-sql-check-sql-agent")

runner = RuleRunner()


@mcp.tool
def get_all_rule_ids() -> list[dict]:
    """获取所有可用的 SQL 规范检查规则列表，返回 rule_id、名称和描述。"""
    result = []
    for rule_id in sorted(RULE_REGISTRY):
        cls = RULE_REGISTRY[rule_id]
        result.append({
            "rule_id": rule_id,
            "name": getattr(cls, "name", ""),
            "desc": getattr(cls, "desc", ""),
        })
    return result


@mcp.tool
def check_sql_compliance(sql: str, rule_list: list[str] = []) -> dict:
    """检查 Spark SQL 是否符合公司内部 SQL 书写规范。

    在生成或修改 SQL 后调用，返回违规报告。
    rule_list 为空时执行所有规则；传入 rule_id 列表则只校验指定规则。

    返回格式：{"passed": bool, "violations": [{"rule": str, "message": str}]}
    """
    return runner.run(sql, rule_list)


if __name__ == "__main__":
    mcp.run()
