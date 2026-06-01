from fastmcp import FastMCP

from checker.runner import RuleRunner

mcp = FastMCP("spark-sql-quality-mcp")

runner = RuleRunner()


@mcp.tool
def check_sql_compliance(sql: str) -> dict:
    """检查 Spark SQL 是否符合公司内部 SQL 书写规范，返回违规报告。

    Agent 不需要、也不能选择具体规则；只需在生成或修改 SQL 后调用本工具进行统一检查。

    硬性违规（error，必须修复）：
    - SQL-DISTINCT-001: 禁止 DISTINCT（含 COUNT(DISTINCT)），请改为 GROUP BY 去重
    - SQL-STAR-001: 禁止 *（SELECT * / COUNT(*) / SUM(*) / t.*），请明确列出字段
    - SQL-FIELD-ALIAS-001: 聚合/计算字段必须有清晰别名，禁用 cnt/num/tmp 等无意义别名
    - SQL-JOIN-RIGHT-001: 禁止 RIGHT JOIN，请调整表顺序改为 LEFT JOIN
    - SQL-JOIN-IMPLICIT-001: 禁止隐式 JOIN（FROM a, b），请改为显式 JOIN ... ON
    - SQL-CROSS-JOIN-001: 禁止 CROSS JOIN，笛卡尔积通常不是业务需要
    - SQL-NULL-COMPARE-001: 禁止 NULL 直接比较（a=NULL），请用 IS NULL / IS NOT NULL / NVL()
    - SQL-NULL-ZERO-001: 除法必须有 NULL 和除零保护，请用 COALESCE(x/NULLIF(y,0),0)
    - SQL-PARTITION-001: 查询必须有分区过滤（pt_d/pt_h/pt_m/pt_w）
    - SQL-CTE-001: 禁止 WITH CTE，请改用临时表（CREATE TABLE tmp_xxx AS ...）
    - SQL-IN-SUBQUERY-001: 禁止 IN (SELECT ...)，请改用 JOIN 或 EXISTS
    - SQL-UNION-001: 禁止 UNION，请改用 UNION ALL（UNION 隐式去重等同于 DISTINCT）

    规范检查（warning，必须符合约定）：
    - SQL-TABLE-ALIAS-001: 多表/JOIN 时字段必须带表别名
    - SQL-SUBQUERY-ALIAS-001: 子查询必须有别名
    - SQL-KEYWORD-CASE-001: SQL 关键词必须大写
    - SQL-CASE-ELSE-001: CASE WHEN 必须包含 ELSE 分支
    - SQL-GROUP-BY-001: 非聚合字段必须在 GROUP BY 中
    - SQL-JOIN-FILTER-001: 分区过滤必须下推到 JOIN 前的子查询
    - SQL-TEMP-TABLE-001: 临时表命名格式: tmp_{业务域}_{描述}_{日期}
    - SQL-ORDER-LIMIT-001: ORDER BY 必须搭配 LIMIT
    - SQL-NEST-DEPTH-001: 子查询嵌套不超过 3 层
    """
    return runner.run(sql)
