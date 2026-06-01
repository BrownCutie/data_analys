# Spark SQL 规范检查 MCP — 技术分享

## 一、项目背景

在日常数据开发中，Spark SQL 是我们最核心的生产语言。无论是数据清洗、指标计算还是报表产出，最终都落到一条条 SQL 上。随着团队规模和业务复杂度的增长，SQL 质量问题逐渐暴露：

- 线上事故中，因 SQL 写法不规范导致的问题占比较高（全表扫描、隐式 JOIN、除零等）
- Code Review 时 SQL 规范检查依赖人工经验，耗时且容易遗漏
- AI Agent 辅助编写 SQL 的场景越来越多，但 Agent 生成的 SQL 不一定符合公司规范

我们需要一个**自动化、标准化、可集成到 AI 工作流**的 SQL 规范检查方案。

## 二、问题痛点

### 2.1 人工审查成本高

一条复杂 SQL 可能涉及数十条规范，Review 时很难逐一检查。不同人关注的规范点不同，检查结果因人而异。新人尤其容易踩坑。

### 2.2 AI 生成的 SQL 不可控

接入 Claude、GPT 等 AI 工具辅助写 SQL 后，生成的代码逻辑上正确但不一定符合公司内部规范（如必须用临时表代替 CTE、必须有分区过滤等）。Agent 不知道我们的规范是什么。

### 2.3 规范落地依赖文档和口口相传

公司 SQL 规范散落在各处文档中，开发时需要主动查阅。没有强制的检查机制，规范执行全靠自觉。

### 2.4 问题发现滞后

不规范 SQL 往往在测试甚至上线阶段才被发现，此时修改成本远高于编写阶段。

## 三、解决方案

### 3.1 整体架构

```
┌─────────────┐     SQL      ┌──────────────────┐     AST      ┌─────────────┐
│  AI Agent   │ ──────────►  │   FastMCP Server  │ ──────────► │   SQLGlot    │
│ (Claude等)  │ ◄────────── │  check_sql_compliance ◄────────── │  Spark 方言   │
└─────────────┘  违规报告    └────────┬─────────┘   解析        └─────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │     RuleRunner       │
                     │  (过滤黑名单 → 依次执行) │
                     └──────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼           ▼           ▼
               ┌─────────┐ ┌─────────┐ ┌─────────┐
               │ 硬性规则  │ │ 硬性规则  │ │  ...共   │
               │ no_distinct│ │no_star  │ │ 21 条   │
               └─────────┘ └─────────┘ └─────────┘
```

### 3.2 核心技术选型

| 组件 | 选型 | 理由 |
|---|---|---|
| 协议层 | FastMCP (MCP 协议) | AI Agent 行业标准协议，Claude/Cursor/OpenCode 等原生支持 |
| SQL 解析 | SQLGlot (Spark 方言) | 纯 Python，无 JVM 依赖，AST 解析能力强 |
| 依赖管理 | uv | 轻量快速，一条命令完成安装和运行 |
| 规则管理 | 自动扫描 + YAML 黑名单 | 新增规则零配置，禁用规则改 YAML 即可 |

### 3.3 MCP 协议集成

MCP（Model Context Protocol）是 Anthropic 推出的 AI Agent 通信协议。通过 MCP，SQL 检查能力可以作为**工具**暴露给任意 AI Agent：

```json
// Agent 调用示例
{
  "tool": "check_sql_compliance",
  "input": {
    "sql": "SELECT DISTINCT user_id FROM t"
  }
}

// 返回结果
{
  "passed": false,
  "violations": [
    {"rule": "SQL-DISTINCT-001", "message": "禁止使用 DISTINCT，请改为 GROUP BY 去重", "severity": "error"},
    {"rule": "SQL-PARTITION-001", "message": "查询缺少分区过滤", "severity": "warning"}
  ]
}
```

Agent 在生成 SQL 后自动调用此工具，根据返回的违规报告修改 SQL，形成**生成 → 检查 → 修改**的闭环。

## 四、解决的问题

### 4.1 硬性违规（12 条，error 级别）

命中即禁止，Agent 会根据报错自动修正：

| 问题 | 规则 | Agent 修正示例 |
|---|---|---|
| `SELECT DISTINCT` 隐式去重 | SQL-DISTINCT-001 | 改为 GROUP BY |
| `SELECT * / COUNT(*)` 不明确 | SQL-STAR-001 | 改为具体字段 / COUNT(1) |
| 聚合字段无别名或别名无意义 | SQL-FIELD-ALIAS-001 | 补充业务含义别名 |
| `RIGHT JOIN` 增加理解成本 | SQL-JOIN-RIGHT-001 | 调整表顺序改为 LEFT JOIN |
| `FROM a, b` 隐式 JOIN | SQL-JOIN-IMPLICIT-001 | 改为显式 JOIN ... ON |
| `CROSS JOIN` 笛卡尔积 | SQL-CROSS-JOIN-001 | 改为 INNER JOIN |
| `a = NULL` 错误判断 | SQL-NULL-COMPARE-001 | 改为 IS NULL / NVL() |
| 除法无保护导致除零 | SQL-NULL-ZERO-001 | 改为 COALESCE(x/NULLIF(y,0),0) |
| 缺少分区过滤全表扫描 | SQL-PARTITION-001 | 补充 pt_d/pt_h/pt_m/pt_w |
| `WITH CTE` 不符合 Spark 规范 | SQL-CTE-001 | 改为临时表 |
| `IN (SELECT ...)` 性能差 | SQL-IN-SUBQUERY-001 | 改为 JOIN |
| `UNION` 隐式去重 | SQL-UNION-001 | 改为 UNION ALL |

### 4.2 规范检查（9 条，warning 级别）

必须符合约定，Agent 会据此调整写法：

| 问题 | 规则 | 说明 |
|---|---|---|
| 多表查询字段不带别名 | SQL-TABLE-ALIAS-001 | 避免同名字段歧义 |
| 子查询无别名 | SQL-SUBQUERY-ALIAS-001 | SQL 语法要求 |
| 关键词小写 | SQL-KEYWORD-CASE-001 | 统一风格提高可读性 |
| CASE WHEN 缺 ELSE | SQL-CASE-ELSE-001 | 避免产生意外 NULL |
| GROUP BY 字段不完整 | SQL-GROUP-BY-001 | 避免数据错误 |
| 分区过滤未下推 | SQL-JOIN-FILTER-001 | 避免全量 JOIN 后再过滤 |
| 临时表命名随意 | SQL-TEMP-TABLE-001 | 统一 tmp_{域}_{描述}_{日期} |
| ORDER BY 无 LIMIT | SQL-ORDER-LIMIT-001 | 避免全量 shuffle |
| 子查询嵌套过深 | SQL-NEST-DEPTH-001 | 超过 3 层拆为临时表 |

## 五、扩展性

### 5.1 新增规则：零配置

只需写一个 Python 文件，不用改任何其他代码：

```python
# checker/hard/join/no_full_join.py
from sqlglot import exp
from checker.base import BaseChecker, CheckContext, Violation

class NoFullJoinChecker(BaseChecker):
    rule_id = "SQL-FULL-JOIN-001"

    def check(self, ctx: CheckContext) -> list[Violation]:
        violations = []
        for stmt in ctx.statements:
            for node in stmt.walk():
                if isinstance(node, exp.Join) and node.kind == "FULL":
                    violations.append(Violation(message="禁止使用 FULL JOIN"))
        return violations
```

`registry.py` 会自动扫描并注册，规则立即生效。

### 5.2 禁用规则：改 YAML

```yaml
# rules.yaml
disabled:
  - SQL-ORDER-LIMIT-001    # 临时关闭
```

### 5.3 主题分组

规则按主题分子目录管理：

```
checker/
├── hard/
│   ├── aggregate/      # 聚合相关
│   ├── select/         # SELECT 相关
│   ├── join/           # JOIN 相关
│   ├── null/           # NULL 处理
│   ├── partition/      # 分区相关
│   ├── cte/            # CTE 相关
│   ├── subquery/       # 子查询相关
│   └── union/          # UNION 相关
└── convention/
    ├── alias/          # 别名规范
    ├── format/         # 格式规范
    ├── aggregate/      # 聚合规范
    ├── join/           # JOIN 规范
    ├── naming/         # 命名规范
    ├── sort/           # 排序规范
    └── subquery/       # 子查询规范
```

新增规则放到对应的主题文件夹下即可。

### 5.4 多客户端支持

MCP 是标准协议，一次部署，多个客户端可用：

- **Claude Code** — `.mcp.json` 配置
- **Cursor** — 设置 → MCP
- **OpenCode** — `opencode.json` 配置
- **任何支持 MCP 的 Agent** — 统一调用 `check_sql_compliance`

## 六、方案优势

### 6.1 左移检查，前置拦截

传统方式：写 SQL → 提交 → Review → 测试 → 上线发现问题（修复成本高）

本方案：AI Agent 写 SQL → **自动检查** → 自动修正 → 代码已符合规范（修复成本趋近于零）

### 6.2 不依赖 JVM，轻量部署

纯 Python 实现，SQLGlot 在 Python 层解析 SQL，不需要 Spark 环境。`uv run` 一条命令启动，无需安装 JDK 或配置 Spark。

### 6.3 规则与工具解耦

- Agent 只看到一个 `check_sql_compliance(sql)` 接口
- 内部 21 条规则可以自由增删改，不影响 Agent 调用方式
- 不同团队可以 fork 后自定义规则集，工具接口不变

### 6.4 AI 原生设计

不是"给人用的 CLI 工具加个 wrapper"，而是从一开始就按 MCP 协议设计。Agent 生成 SQL 后天然会调用检查工具，形成**写代码 → 查规范 → 改代码**的闭环，规范检查从被动审查变为主动修正。

### 6.5 渐进式采用

- **最低门槛**：AI Agent 自动检查，开发零感知
- **进阶使用**：CI/CD 中集成 `uv run pytest`，拦截不合规 SQL
- **灵活定制**：通过 `rules.yaml` 关闭不需要的规则，逐步推广

---

## 快速开始

```bash
git clone git@github.com:BrownCutie/data_analys.git
cd data_analys/spark-sql-quality

# 验证是否正常工作
uv run python3 -c "
from checker.runner import RuleRunner
import json
runner = RuleRunner()
print(json.dumps(runner.run('SELECT DISTINCT * FROM t'), ensure_ascii=False, indent=2))
"

# 运行测试
uv run pytest tests/ -v
```

详细配置和规则说明参见 [README](README.md)。
