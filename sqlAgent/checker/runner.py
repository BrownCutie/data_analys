from __future__ import annotations

import logging

import sqlglot

from checker.base import CheckContext, Violation
from checker.registry import RULE_REGISTRY
from config import load_disabled_rules

logger = logging.getLogger(__name__)


class RuleRunner:
    def __init__(self) -> None:
        disabled = load_disabled_rules()
        self.checker_ids = [rid for rid in RULE_REGISTRY if rid not in disabled]

    def run(self, sql: str) -> dict:
        # 1. parse
        try:
            statements = sqlglot.parse(sql, read="spark")
        except sqlglot.errors.ParseError as e:
            return {"passed": False, "violations": [], "parse_error": str(e)}

        # 2. check
        ctx = CheckContext(raw_sql=sql, statements=statements)
        results: list[dict] = []
        for rule_id in self.checker_ids:
            checker = RULE_REGISTRY[rule_id]()
            try:
                for v in checker.check(ctx):
                    results.append({"rule": rule_id, "message": v.message, "severity": v.severity})
            except Exception:
                logger.exception("Checker %s 执行异常", rule_id)

        # 3. result
        return {"passed": len(results) == 0, "violations": results}
