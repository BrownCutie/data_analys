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
cd data_analys
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

以下配置中 `PROJECT_DIR` 替换为实际路径，例如 `/Users/browncutie/Programme/data_analysis`。

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

| 规则 ID | 检查内容 | 级别 |
|---|---|---|
| SQL-DISTINCT-001 | 禁止 DISTINCT | error |
| SQL-COUNT-001 | 禁止 COUNT(*) | error |
| SQL-COUNT-DISTINCT-001 | 禁止 COUNT(DISTINCT ...) | error |
| SQL-PARTITION-001 | 必须包含 pt_d/pt_h 分区过滤 | error |
| SQL-JOIN-RIGHT-001 | 禁止 RIGHT JOIN | error |
| SQL-SUBQUERY-ALIAS-001 | 子查询必须有别名 | error |
| SQL-FIELD-ALIAS-001 | 多表查询字段必须带表别名 | warning |

## 如何新增一条检查规则

### 第 1 步：写 Checker

在 `checker/` 下新建文件，例如 `no_select_star.py`：

```python
from sqlglot import exp
from checker.base import BaseChecker, CheckContext, Violation


class NoSelectStarChecker(BaseChecker):
    rule_id = "SQL-SELECT-STAR-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Star):
                    violations.append(Violation(
                        rule=self.rule_id,
                        message="禁止 SELECT *，请明确列出字段",
                    ))
        return violations
```

### 第 2 步：注册并启用

在 `checker/registry.py` 中添加一行：

```python
from checker.no_select_star import NoSelectStarChecker

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
