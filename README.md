# Data Analysis MCP Tools

两个独立的 MCP 项目，分别维护在不同分支。

| 分支 | 项目 | 说明 |
|---|---|---|
| `spark-sql-quality` | SQL 规范检查 | FastMCP + SQLGlot，14 条规则，硬性违规 + 规范检查 |
| `platform-api` | 平台 API 调用 | FastMCP + httpx + Playwright，cookie 自动续期 |

```bash
git clone -b spark-sql-quality git@github.com:BrownCutie/data_analys.git spark-sql-quality
git clone -b platform-api git@github.com:BrownCutie/data_analys.git platform-api
```
