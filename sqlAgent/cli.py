"""Spark SQL 规范检查 CLI（sqlAgent 版本）

用法:
  uv run --directory /path/to/spark-sql-check-mcp-server/sqlAgent python cli.py "SELECT * FROM t"
  uv run --directory /path/to/spark-sql-check-mcp-server/sqlAgent python cli.py -f query.sql
  uv run --directory /path/to/spark-sql-check-mcp-server/sqlAgent python cli.py -f query.sql --quiet
"""

from __future__ import annotations

import json
import sys

from checker.runner import RuleRunner


def main() -> None:
    sql: str | None = None
    filepath: str | None = None
    quiet: bool = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "-f" and i + 1 < len(args):
            filepath = args[i + 1]
            i += 2
        elif args[i] == "--quiet":
            quiet = True
            i += 1
        elif args[i] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif not sql:
            sql = args[i]
            i += 1
        else:
            print(f"未知参数: {args[i]}", file=sys.stderr)
            sys.exit(2)

    if filepath:
        with open(filepath) as f:
            sql = f.read().strip()
    elif not sql:
        print("用法: python cli.py \"SQL\" 或 python cli.py -f file.sql", file=sys.stderr)
        sys.exit(2)

    runner = RuleRunner()
    result = runner.run(sql)

    if result["passed"]:
        if not quiet:
            print("PASS")
        sys.exit(0)
    else:
        if quiet:
            print("FAIL")
        else:
            print(f"FAIL — {len(result['violations'])} 条违规:")
            for v in result["violations"]:
                print(f"  [{v['severity'].upper()}] {v['rule']}: {v['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
