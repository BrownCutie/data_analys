# CLAUDE.md — 项目上下文

## 项目简介
Spark SQL 公司规范检查 MCP 服务。基于 FastMCP + SQLGlot，对外暴露一个工具 `check_sql_compliance`，Agent 传入 SQL 即可获得违规报告。

## 技术栈
- Python + FastMCP + SQLGlot（Spark 方言）
- uv 管理依赖，pytest 测试

## 目录结构
```
server.py              # MCP 入口
config.py              # 加载 rules.yaml（黑名单）
rules.yaml             # 禁用的规则列表，默认全执行
checker/
├── base.py            # BaseChecker, CheckContext, Violation
├── registry.py        # 自动扫描 hard/convention 下所有 .py，找 BaseChecker 子类
├── runner.py          # 全量规则减去 disabled，依次执行
├── hard/              # 硬性违规（命中即禁止）
│   └── ...            # 每个 checker 一个 .py 文件
└── convention/        # 规范检查（必须符合约定）
    └── ...            # 每个 checker 一个 .py 文件
```

## 核心设计
- **registry.py 自动扫描**：递归扫描 hard/ 和 convention/ 下所有 .py（含子目录），找到 BaseChecker 子类自动注册。新增规则只需写 .py 文件。
- **rules.yaml 黑名单**：默认所有规则都执行，yaml 里只配不需要的（disabled 列表）。
- **runner.py**：从 registry 拿全量规则，减去 disabled，依次执行 checker.check()，汇总结果。
- **单一 MCP Tool**：对外只暴露 `check_sql_compliance(sql)`，Agent 不能选择规则。

## 新增规则
1. 在 checker/hard/ 或 checker/convention/ 下（含任意子目录）新建 .py 文件
2. 继承 BaseChecker，声明 rule_id，实现 check(ctx) 方法
3. 不用改 registry、不用改 yaml，自动生效

## 关闭规则
在 rules.yaml 的 disabled 列表中加 rule_id

## 常用命令
```bash
uv run pytest tests/ -v          # 跑测试
uv run fastmcp run server.py     # 启动 MCP 服务
```

## Checker 文件模板
每个 checker 文件头部有标准注释：触发关键字、核心目标、违规示例、正确写法。
所有 checker 使用绝对导入：`from checker.base import BaseChecker, CheckContext, Violation`
