# Spark SQL 规范检查 MCP — 需求文档

## 项目概述

一个基于 FastMCP 的 SQL 规范检查服务。对外只暴露一个 Tool `check_sql_compliance`，Agent 只需传入 SQL，内部按配置执行所有检查规则，返回违规列表。

**技术栈**: Python + FastMCP + SQLGlot（Spark 方言）

---

## 对外接口

### 输入

```json
{ "sql": "SELECT ..." }
```

只有一个参数 `sql`，Agent 不能选择规则、不能指定方言、不能控制任何内部行为。

### 输出

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

**说明**：
- `passed`: 是否全部通过
- `violations`: 违规列表，每条只有三个字段：规则ID、说明、严重级别
- SQL 解析失败时 `violations` 为空，`passed` 为 false，额外返回 `parse_error` 字段

---

## 项目结构

```
sql_quality_mcp/
├── server.py              # FastMCP 入口
├── checker/
│   ├── base.py            # BaseChecker 接口
│   ├── registry.py        # 规则注册器
│   ├── runner.py          # 按配置顺序执行所有 checker
│   ├── no_distinct.py
│   ├── no_count_star.py
│   └── ...                # 每个 checker 一个文件
├── config.py              # 加载 rules.yaml
└── rules.yaml             # 启用哪些规则
```

---

## 如何新增一条检查规则

只需两步：

### 第 1 步：写 Checker

在 `checker/` 目录下新建文件，例如 `no_select_star.py`：

```python
from checker.base import BaseChecker, CheckContext, Violation

class NoSelectStarChecker(BaseChecker):
    rule_id = "SQL-SELECT-STAR-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for select in stmt.find_all(exp.Select):
                for expr in select.expressions:
                    if isinstance(expr, exp.Star):
                        violations.append(Violation(
                            rule=self.rule_id,
                            message="禁止 SELECT *，请明确列出字段",
                            severity="error",
                        ))
        return violations
```

### 第 2 步：注册并启用

在 `checker/registry.py` 中注册：

```python
from checker.no_select_star import NoSelectStarChecker

RULE_REGISTRY = {
    "SQL-SELECT-STAR-001": NoSelectStarChecker,
    # ... 其他规则
}
```

在 `rules.yaml` 中启用：

```yaml
enabled:
  - SQL-SELECT-STAR-001
```

完成。不需要改 MCP Tool、不需要改任何其他文件。

---

## BaseChecker 接口

所有 Checker 继承这个基类：

```python
class BaseChecker:
    rule_id: str          # 如 "SQL-DISTINCT-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        raise NotImplementedError
```

**Checker 守则**：
- 从 `ctx.statements`（SQLGlot AST）做检查，不要自己 parse SQL
- 只返回违规列表，没违规就返回空列表
- 异常由 Runner 捕获处理，Checker 内部不要吞掉异常也不要往外抛

---

## 配置文件 rules.yaml

```yaml
enabled:
  - SQL-DISTINCT-001
  - SQL-COUNT-001
  - SQL-COUNT-DISTINCT-001
  - SQL-PARTITION-001
  - SQL-JOIN-RIGHT-001
  - SQL-SUBQUERY-ALIAS-001
  - SQL-FIELD-ALIAS-001
```

`enabled` 的顺序就是执行顺序。不需要的规则直接注释或删掉。

---

## 第一阶段要实现的规则

| 规则 ID | 检查内容 | 级别 |
|---|---|---|
| SQL-DISTINCT-001 | 禁止 DISTINCT，用 GROUP BY 去重 | error |
| SQL-COUNT-001 | 禁止 COUNT(*)，用 COUNT(1) | error |
| SQL-COUNT-DISTINCT-001 | 禁止 COUNT(DISTINCT x)，内层 GROUP BY + 外层 COUNT(1) | error |
| SQL-PARTITION-001 | WHERE 中必须包含 pt_d 或 pt_h 分区过滤 | error |
| SQL-JOIN-RIGHT-001 | 禁止 RIGHT JOIN，改为 LEFT JOIN 调整表顺序 | error |
| SQL-SUBQUERY-ALIAS-001 | 子查询必须有别名 | error |
| SQL-FIELD-ALIAS-001 | 多表查询时字段引用必须带表别名 | warning |

---

## 错误处理

- **SQL 解析失败**: 不执行任何 checker，返回 `passed=false` + `parse_error` 信息
- **单条规则异常**: 跳过该规则，继续执行后续规则
- **配置了未注册的规则**: 启动时报错

---

## 约束

- 只支持 Spark SQL，硬编码 `read="spark"`
- 不执行 SQL、不连数据库、不做血缘分析
- 不自动修复 SQL，只返回违规信息
- SQL 只解析一次，所有 checker 共享 AST

---

## 依赖

```
fastmcp
sqlglot
pyyaml
```

Python >= 3.11
