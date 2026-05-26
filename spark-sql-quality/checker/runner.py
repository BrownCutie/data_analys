from __future__ import annotations

import logging

import sqlglot

from .base import BaseChecker, CheckContext, Violation
from .registry import RULE_REGISTRY
from config import load_enabled_rules

logger = logging.getLogger(__name__)


class RuleRunner:
    def __init__(self) -> None:
        self.enabled_ids = load_enabled_rules()
        unregistered = [r for r in self.enabled_ids if r not in RULE_REGISTRY]
        if unregistered:
            raise RuntimeError(f"未注册的规则: {unregistered}")

    def run(self, sql: str) -> dict:
        # 1. parse
        try:
            statements = sqlglot.parse(sql, read="spark")
        except sqlglot.errors.ParseError as e:
            return {"passed": False, "violations": [], "parse_error": str(e)}

        # 2. check
        ctx = CheckContext(raw_sql=sql, statements=statements)
        results: list[dict] = []
        for rule_id in self.enabled_ids:
            checker = RULE_REGISTRY[rule_id]()
            try:
                for v in checker.check(ctx):
                    results.append({"rule": rule_id, "message": v.message, "severity": v.severity})
            except Exception:
                logger.exception("Checker %s 执行异常", rule_id)

        # 3. result
        return {"passed": len(results) == 0, "violations": results}
