# Spark SQL 规范检查 MCP

基于 FastMCP + SQLGlot 的 Spark SQL 公司规范检查服务。支持 MCP 工具（AI Agent 调用）和 CLI（终端/CI 直接使用）两种模式。

## 安装

需要先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：

```bash
# macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

克隆项目：

```bash
git clone git@github.com:BrownCutie/data_analys.git
cd data_analys/spark-sql-check-mcp-server
```

## 使用方式

### 方式一：MCP 工具（AI Agent 自动检查）

配置 MCP 客户端后，Agent 在生成 SQL 时会自动调用 `check_sql_compliance` 工具进行检查。

配置中 `PROJECT_DIR` 替换为项目绝对路径，例如 `/Users/xxx/data_analys/spark-sql-check-mcp-server`。

#### OpenCode

编辑 `~/.config/opencode/opencode.json`：

```json
{
  "mcpServers": {
    "spark-sql-check-mcp-server": {
      "command": "uv",
      "args": ["run", "--directory", "PROJECT_DIR", "fastmcp", "run", "server.py"]
    }
  }
}
```

或用 CLI：

```bash
opencode mcp add
# Name: spark-sql-check-mcp-server
# Type: local
# Command: uv run --directory PROJECT_DIR fastmcp run server.py
```

> 另一台电脑配置方式相同，把 `PROJECT_DIR` 换成那台电脑上的项目路径即可。
> 前提：那台电脑需要先 `git clone` 项目并安装 `uv`。

#### Claude Code

在项目目录下创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "spark-sql-check-mcp-server": {
      "command": "uv",
      "args": ["run", "--directory", "PROJECT_DIR", "fastmcp", "run", "server.py"]
    }
  }
}
```

#### Cursor

设置 → MCP → Add new MCP Server：

| 字段 | 值 |
|---|---|
| Name | spark-sql-check-mcp-server |
| Type | command |
| Command | `uv run --directory PROJECT_DIR fastmcp run server.py` |

### 方式二：CLI（终端 / CI / pre-commit hook）

```bash
# 直接检查 SQL
uv run --directory PROJECT_DIR python cli.py "SELECT DISTINCT user_id FROM t"

# 从文件读取
uv run --directory PROJECT_DIR python cli.py -f query.sql

# 静默模式（只输出 PASS/FAIL，适合 CI 判断）
uv run --directory PROJECT_DIR python cli.py -f query.sql --quiet
echo $?  # 0=通过, 1=违规

# 在当前项目目录下可省略 --directory
cd /path/to/spark-sql-check-mcp-server
uv run python cli.py "SELECT * FROM t"
```

#### pre-commit hook 配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: sql-compliance
        entry: uv run --directory /path/to/spark-sql-check-mcp-server python cli.py -f
        language: system
        files: \.sql$
```

## 快速验证

```bash
# CLI 验证
uv run python cli.py "SELECT DISTINCT * FROM t WHERE pt_d = '20260101'"
```

输出示例：

```
FAIL — 2 条违规:
  [ERROR] SQL-DISTINCT-001: 禁止使用 DISTINCT，请改为 GROUP BY 去重
  [ERROR] SQL-STAR-001: 禁止 SELECT *，请明确列出需要的字段
```

## 项目结构

```
server.py              # MCP 入口，注册 check_sql_compliance 工具
cli.py                # CLI 入口，支持直接检查和文件读取
config.py              # 加载 rules.yaml（黑名单机制）
rules.yaml             # 禁用规则列表，默认全部执行
checker/
├── base.py            # BaseChecker, CheckContext, Violation
├── registry.py        # 自动扫描 hard/convention 下所有 .py，按 rule_id 注册
├── runner.py          # 过滤黑名单 → 解析 SQL → 依次执行 checker → 汇总结果
├── hard/              # 硬性违规（命中即禁止）
│   ├── aggregate/
│   │   ├── no_distinct.py
│   │   └── field_alias.py
│   ├── select/
│   │   └── no_star_usage.py
│   ├── join/
│   │   ├── no_right_join.py
│   │   ├── no_implicit_join.py
│   │   └── no_cross_join.py
│   ├── null/
│   │   ├── no_null_direct_compare.py
│   │   └── null_zero.py
│   ├── partition/
│   │   └── partition_required.py
│   ├── cte/
│   │   └── no_cte.py
│   ├── subquery/
│   │   └── no_in_subquery.py
│   └── union/
│       └── no_union.py
└── convention/        # 规范检查（必须符合约定）
    ├── alias/
    │   ├── table_alias.py
    │   └── subquery_alias.py
    ├── format/
    │   ├── keyword_uppercase.py
    │   └── case_when_else.py
    ├── aggregate/
    │   └── group_by.py
    ├── join/
    │   └── join_filter_first.py
    ├── naming/
    │   └── temp_table_naming.py
    ├── sort/
    │   └── order_by_limit.py
    └── subquery/
        └── subquery_depth.py
```

## 当前启用的规则

### 硬性违规项（error，命中即禁止，必须修复）

| 规则 ID | 触发关键字 | 文件 | 核心目标 |
|---|---|---|---|
| SQL-DISTINCT-001 | DISTINCT, COUNT(DISTINCT) | `aggregate/no_distinct.py` | 消除 DISTINCT 写法，改为 GROUP BY |
| SQL-STAR-001 | SELECT *, COUNT(*), SUM(*), t.* | `select/no_star_usage.py` | 禁止所有 * 用法，明确列出字段 |
| SQL-FIELD-ALIAS-001 | 聚合/CASE WHEN/计算字段 | `aggregate/field_alias.py` | 须有清晰别名，禁用 cnt/num/tmp 等 |
| SQL-JOIN-RIGHT-001 | RIGHT JOIN | `join/no_right_join.py` | 消除 RIGHT JOIN，改用 LEFT JOIN |
| SQL-JOIN-IMPLICIT-001 | FROM a, b WHERE a.id=b.id | `join/no_implicit_join.py` | 改为显式 JOIN ... ON |
| SQL-CROSS-JOIN-001 | CROSS JOIN | `join/no_cross_join.py` | 禁止笛卡尔积 |
| SQL-NULL-COMPARE-001 | a=NULL, a>NULL | `null/no_null_direct_compare.py` | 改用 IS NULL / IS NOT NULL / NVL() |
| SQL-NULL-ZERO-001 | 除法运算 | `null/null_zero.py` | COALESCE(x/NULLIF(y,0),0) 保护 |
| SQL-PARTITION-001 | 查询 Hive 表/明细表 | `partition/partition_required.py` | 必须有分区过滤(pt_d/pt_h/pt_m/pt_w) |
| SQL-CTE-001 | WITH ... AS (SELECT ...) | `cte/no_cte.py` | 禁止 CTE，改用临时表 |
| SQL-IN-SUBQUERY-001 | IN (SELECT ...) | `subquery/no_in_subquery.py` | 改用 JOIN 或 EXISTS |
| SQL-UNION-001 | UNION（不带 ALL） | `union/no_union.py` | 改用 UNION ALL |

### 规范检查项（warning，必须符合约定）

| 规则 ID | 触发关键字 | 文件 | 核心目标 |
|---|---|---|---|
| SQL-TABLE-ALIAS-001 | 多表/JOIN/子查询 | `alias/table_alias.py` | 字段引用必须带表别名 |
| SQL-SUBQUERY-ALIAS-001 | FROM/JOIN 后有嵌套 SELECT | `alias/subquery_alias.py` | 子查询必须有别名 |
| SQL-KEYWORD-CASE-001 | SQL 关键词 | `format/keyword_uppercase.py` | 所有关键词必须大写 |
| SQL-CASE-ELSE-001 | CASE WHEN | `format/case_when_else.py` | 必须包含 ELSE 分支 |
| SQL-GROUP-BY-001 | 出现聚合函数 | `aggregate/group_by.py` | 非聚合字段须全在 GROUP BY 中 |
| SQL-JOIN-FILTER-001 | JOIN 大表/明细表 | `join/join_filter_first.py` | 分区过滤下推至子查询 |
| SQL-TEMP-TABLE-001 | CREATE/INSERT 含 tmp_ | `naming/temp_table_naming.py` | 格式: tmp\_{业务域}\_{描述}\_{日期} |
| SQL-ORDER-LIMIT-001 | ORDER BY | `sort/order_by_limit.py` | 必须搭配 LIMIT |
| SQL-NEST-DEPTH-001 | 嵌套子查询 | `subquery/subquery_depth.py` | 嵌套不超过 3 层 |

## 如何新增规则

只需 **一步**：在 `checker/hard/` 或 `checker/convention/` 下新建 `.py` 文件，继承 `BaseChecker` 即可自动生效。

```python
from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoCrossJoinChecker(BaseChecker):
    rule_id = "SQL-CROSS-JOIN-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Join) and node.kind == "CROSS":
                    violations.append(
                        Violation(message="禁止使用 CROSS JOIN")
                    )
        return violations
```

不用改 registry、不用改 yaml，新增的 `.py` 文件会被自动扫描注册。

## 如何关闭规则

编辑 `rules.yaml`，在 `disabled` 列表中添加 `rule_id`：

```yaml
disabled:
  - SQL-FIELD-ALIAS-001    # 暂时关闭字段别名检查
  # - SQL-TEMP-TABLE-001   # 注释掉即恢复执行
```

## 运行测试

```bash
uv run pytest tests/ -v
```
