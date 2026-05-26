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
# 测试一下
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

## 当前启用的规则

### 一、硬性违规项（命中即禁止，必须修复）

| 规则 ID | 触发关键字 | 文件 | 核心目标 |
|---|---|---|---|
| SQL-DISTINCT-001 | DISTINCT, COUNT(DISTINCT) | `checker/hard/no_distinct.py` | 消除 DISTINCT 写法 |
| SQL-COUNT-001 | COUNT(*) | `checker/hard/no_count_star.py` | 消除 COUNT(*) 写法 |
| SQL-COUNT-DISTINCT-001 | COUNT(DISTINCT ...) | `checker/hard/no_count_distinct.py` | 消除 COUNT(DISTINCT) 写法 |
| SQL-JOIN-RIGHT-001 | RIGHT JOIN | `checker/hard/no_right_join.py` | 消除 RIGHT JOIN |
| SQL-JOIN-IMPLICIT-001 | FROM a, b WHERE a.id=b.id | `checker/hard/no_implicit_join.py` | 改为显式 JOIN ... ON |
| SQL-SELECT-STAR-001 | SELECT * | `checker/hard/no_select_star.py` | 改为显式字段 |

### 二、规范检查项（必须检查是否符合约定）

| 规则 ID | 触发关键字 | 文件 | 核心目标 |
|---|---|---|---|
| SQL-TABLE-ALIAS-001 | 多表/JOIN/子查询 | `checker/convention/table_alias.py` | 所有表必须有别名，字段引用必须带别名 |
| SQL-SUBQUERY-ALIAS-001 | FROM/JOIN 后有嵌套 SELECT | `checker/convention/subquery_alias.py` | 子查询必须有别名，符合 t0, t1... 顺序约定 |
| SQL-FIELD-ALIAS-001 | 聚合/CASE WHEN/计算字段 | `checker/convention/field_alias.py` | 须有清晰别名，禁用 cnt/num1/aaa 等无意义词 |
| SQL-TEMP-TABLE-001 | CREATE/INSERT 含 tmp_ | `checker/convention/temp_table_naming.py` | 推荐格式: tmp\_{业务域}\_{描述}\_{日期} |
| SQL-PARTITION-001 | 查询 Hive 表/明细表 | `checker/convention/partition_filter.py` | 必须有分区过滤(pt_d/pt_h)，条件需下推 |
| SQL-JOIN-FILTER-001 | JOIN 大表/明细表 | `checker/convention/join_filter_first.py` | 必须先过滤后关联，条件下推至子查询 |
| SQL-GROUP-BY-001 | 出现聚合函数 | `checker/convention/group_by.py` | 非聚合字段须全在 GROUP BY 中 |
| SQL-NULL-ZERO-001 | 除法/比率/金额计算 | `checker/convention/null_zero.py` | 必须用 COALESCE(x/NULLIF(y,0),0) 做 NULL 和除零保护 |

## 如何新增一条检查规则

### 第 1 步：写 Checker

在 `checker/hard/`（硬性规则）或 `checker/convention/`（规范检查）下新建文件：

```python
"""
硬性规则 - 禁止 SELECT *

触发关键字: SELECT *
核心目标: 必须显式列出字段，不允许 SELECT *
正确写法: 明确写出所有需要的字段名

违规: SELECT * FROM t
正确: SELECT t.user_id, t.order_id FROM t
"""
from sqlglot import exp
from checker.base import BaseChecker, CheckContext, Violation


class NoSelectStarChecker(BaseChecker):
    rule_id = "SQL-SELECT-STAR-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        ...
```

### 第 2 步：注册并启用

在 `checker/registry.py` 中添加：

```python
from checker.hard.no_select_star import NoSelectStarChecker

RULE_REGISTRY = {
    # ... 已有规则
    "SQL-SELECT-STAR-001": NoSelectStarChecker,
}
```

在 `rules.yaml` 中添加：

```yaml
enabled:
  # ... 已有规则
  - SQL-SELECT-STAR-001
```

完成。不需要改 MCP Tool 或任何其他文件。

## 如何关闭某条规则

编辑 `rules.yaml`，注释或删除对应行：

```yaml
enabled:
  # - SQL-FIELD-ALIAS-001  # 暂时关闭字段别名检查
```

## 运行测试

```bash
uv run pytest tests/ -v
```
