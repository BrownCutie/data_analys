# Data Analysis MCP Tools

数据分析团队内部 MCP 工具集合，用于提升 Agent 辅助开发时的 SQL 和数据质量。

## 项目列表

| 项目 | 说明 |
|---|---|
| [spark-sql-quality](./spark-sql-quality/) | Spark SQL 公司规范检查 MCP — 14 条规则，硬性违规 + 规范检查 |
| [platform-api](./platform-api/) | 平台 API 调用 MCP — Playwright 登录 + cookie 自动续期 |

## 在 OpenCode 中配置

编辑 `~/.config/opencode/opencode.json`，把两个 MCP 都加进去：

```json
{
  "mcp": {
    "spark-sql-quality": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/Users/browncutie/Programme/data_analysis/spark-sql-quality", "fastmcp", "run", "server.py"]
    },
    "platform-api": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/Users/browncutie/Programme/data_analysis/platform-api", "fastmcp", "run", "server.py"]
    }
  }
}
```

或用 CLI 添加：

```bash
# SQL 规范检查
opencode mcp add
# Name: spark-sql-quality
# Type: local
# Command: uv run --directory /Users/browncutie/Programme/data_analysis/spark-sql-quality fastmcp run server.py

# 平台 API
opencode mcp add
# Name: platform-api
# Type: local
# Command: uv run --directory /Users/browncutie/Programme/data_analysis/platform-api fastmcp run server.py
```

重启 OpenCode 后生效。

## 在 Claude Code 中配置

项目目录下创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "spark-sql-quality": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/browncutie/Programme/data_analysis/spark-sql-quality", "fastmcp", "run", "server.py"]
    },
    "platform-api": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/browncutie/Programme/data_analysis/platform-api", "fastmcp", "run", "server.py"]
    }
  }
}
```

## 前置要求

安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

克隆后各项目依赖自动管理，无需手动 pip install。

```bash
git clone git@github.com:BrownCutie/data_analys.git
cd data_analys
```
