# Spark SQL 规范检查 MCP

基于 FastMCP + SQLGlot 的 Spark SQL 公司规范检查服务。对外只暴露一个工具 `check_sql_compliance`，Agent 传入 SQL 即可获得违规报告。

## 安装

需要先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：

```bash
# macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

克隆项目后，依赖自动管理，无需手动 pip install：

```bash
git clone git@github.com:BrownCutie/data_analys.git
cd data_analys/spark-sql-quality
```

## 快速验证

```bash
uv run python3 -c "
from checker.runner import RuleRunner
import json
runner = RuleRunner()
result = runner.run('SELECT DISTINCT user_id FROM t')
print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

输出示例：

```json
{
  "passed": false,
  "violations": [
    {
      "rule": "SQL-DISTINCT-001",
      "message": "禁止使用 DISTINCT，请改为 GROUP BY 去重",
      "severity": "error"
    },
    {
      "rule": "SQL-PARTITION-001",
      "message": "查询缺少分区过滤，WHERE 中必须包含 pt_d 或 pt_h 条件",
      "severity": "error"
    }
  ]
}
```

## 配置 MCP 客户端

以下配置中 `PROJECT_DIR` 替换为实际路径，例如 `/Users/browncutie/Programme/data_analysis/spark-sql-quality`。

### OpenCode

编辑 `~/.config/opencode/opencode.json`：

```json
{
  "mcp": {
    "spark-sql-quality": {
      "type": "local",
      "command": ["uv", "run", "--directory", "PROJECT_DIR", "fastmcp", "run", "server.py"]
    }
  }
}
```

或用 CLI：

```bash
opencode mcp add
# Name: spark-sql-quality
# Type: local
# Command: uv run --directory PROJECT_DIR fastmcp run server.py
```

重启 OpenCode 后生效。

### Claude Code

在项目目录下创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "spark-sql-quality": {
      "command": "uv",
      "args": ["run", "--directory", "PROJECT_DIR", "fastmcp", "run", "server.py"]
    }
  }
}
```

### Cursor

设置 → MCP → Add new MCP Server：

| 字段 | 值 |
|---|---|
| Name | spark-sql-quality |
| Type | command |
| Command | `uv run --directory PROJECT_DIR fastmcp run server.py` |

## 项目结构

```
server.py              # MCP 入口，注册 check_sql_compliance 工具
config.py              # 加载 rules.yaml（黑名单机制）
rules.yaml             # 禁用规则列表，默认全部执行
checker/
├── base.py            # BaseChecker, CheckContext, Violation
├── registry.py        # 自动扫描 hard/convention 下所有 .py，按 rule_id 注册
├── runner.py          # 过滤黑名单 → 解析 SQL → 依次执行 checker → 汇总结果
├── hard/              # 硬性违规（命中即禁止）
│   ├── no_count_distinct.py
│   ├── no_count_star.py
│   ├── no_distinct.py
│   ├── no_implicit_join.py
│   ├── no_right_join.py
│   └── no_select_star.py
└── convention/        # 规范检查（必须符合约定）
    ├── field_alias.py
    ├── group_by.py
    ├── join_filter_first.py
    ├── null_zero.py
    ├── partition_filter.py
    ├── subquery_alias.py
    ├── table_alias.py
    └── temp_table_naming.py
```

## 当前启用的规则

### 硬性违规项（命中即禁止，必须修复）

| 规则 ID | 触发关键字 | 文件 | 核心目标 |
|---|---|---|---|
| SQL-DISTINCT-001 | DISTINCT, COUNT(DISTINCT) | `no_distinct.py` | 消除 DISTINCT 写法 |
| SQL-COUNT-001 | COUNT(*) | `no_count_star.py` | 消除 COUNT(*) 写法 |
| SQL-COUNT-DISTINCT-001 | COUNT(DISTINCT ...) | `no_count_distinct.py` | 消除 COUNT(DISTINCT) 写法 |
| SQL-JOIN-RIGHT-001 | RIGHT JOIN | `no_right_join.py` | 消除 RIGHT JOIN |
| SQL-JOIN-IMPLICIT-001 | FROM a, b WHERE a.id=b.id | `no_implicit_join.py` | 改为显式 JOIN ... ON |
| SQL-SELECT-STAR-001 | SELECT * | `no_select_star.py` | 改为显式字段 |

### 规范检查项（必须符合约定）

| 规则 ID | 触发关键字 | 文件 | 核心目标 |
|---|---|---|---|
| SQL-TABLE-ALIAS-001 | 多表/JOIN/子查询 | `table_alias.py` | 所有表必须有别名，字段引用必须带别名 |
| SQL-SUBQUERY-ALIAS-001 | FROM/JOIN 后有嵌套 SELECT | `subquery_alias.py` | 子查询必须有别名 |
| SQL-FIELD-ALIAS-001 | 聚合/CASE WHEN/计算字段 | `field_alias.py` | 须有清晰别名，禁用 cnt/num1/aaa 等无意义词 |
| SQL-TEMP-TABLE-001 | CREATE/INSERT 含 tmp_ | `temp_table_naming.py` | 推荐格式: tmp\_{业务域}\_{描述}\_{日期} |
| SQL-PARTITION-001 | 查询 Hive 表/明细表 | `partition_filter.py` | 必须有分区过滤(pt_d/pt_h)，条件需下推 |
| SQL-JOIN-FILTER-001 | JOIN 大表/明细表 | `join_filter_first.py` | 必须先过滤后关联，条件下推至子查询 |
| SQL-GROUP-BY-001 | 出现聚合函数 | `group_by.py` | 非聚合字段须全在 GROUP BY 中 |
| SQL-NULL-ZERO-001 | 除法/比率/金额计算 | `null_zero.py` | 必须用 COALESCE(x/NULLIF(y,0),0) 做 NULL 和除零保护 |

## 如何新增规则

只需 **一步**：在 `checker/hard/` 或 `checker/convention/` 下新建 `.py` 文件，继承 `BaseChecker` 即可自动生效。

```python
"""
硬性规则 - 禁止 SELECT *

触发关键字: SELECT *
核心目标: 必须显式列出字段，不允许 SELECT *
违规示例: SELECT * FROM t
正确写法: SELECT t.user_id, t.order_id FROM t
"""
from sqlglot import exp

from checker.base import BaseChecker, CheckContext, Violation


class NoSelectStarChecker(BaseChecker):
    rule_id = "SQL-SELECT-STAR-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                for expr in select.expressions:
                    if isinstance(expr, exp.Star):
                        violations.append(
                            Violation(message="禁止使用 SELECT *，请显式列出字段")
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
