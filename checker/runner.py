from __future__ import annotations

import logging

import sqlglot

from checker.base import BaseChecker, CheckContext, Violation
from checker.registry import RULE_REGISTRY
from config import load_enabled_rules

logger = logging.getLogger(__name__)


class RuleRunner:
    def __init__(self) -> None:
        self.enabled_ids = load_enabled_rules()
        unregistered = [r for r in self.enabled_ids if r not in RULE_REGISTRY]
        if unregistered:
            raise RuntimeError(f"未注册的规则: {unregistered}")
        self.checkers: list[BaseChecker] = [RULE_REGISTRY[rid]() for rid in self.enabled_ids]

    def run(self, sql: str) -> dict:
        # 1. parse
        try:
            statements = sqlglot.parse(sql, read="spark")
        except sqlglot.errors.ParseError as e:
            return {"passed": False, "violations": [], "parse_error": str(e)}

        # 2. check
        ctx = CheckContext(raw_sql=sql, statements=statements)
        violations: list[Violation] = []
        for checker in self.checkers:
            try:
                violations.extend(checker.check(ctx))
            except Exception:
                logger.exception("Checker %s 执行异常", checker.rule_id)

        # 3. result
        return {
            "passed": len(violations) == 0,
            "violations": [{"rule": v.rule, "message": v.message, "severity": v.severity} for v in violations],
        }
