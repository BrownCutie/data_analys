from __future__ import annotations

import logging

import sqlglot

from checker.base import CheckContext, Violation
from checker.registry import RULE_REGISTRY

logger = logging.getLogger(__name__)


class RuleRunner:
    def __init__(self) -> None:
        self.checker_ids = list(RULE_REGISTRY.keys())

    def run(self, sql: str, rule_list: list[str] | None = None) -> dict:
        # 1. parse
        try:
            statements = sqlglot.parse(sql, read="spark")
        except sqlglot.errors.ParseError as e:
            return {"passed": False, "violations": [], "parse_error": str(e)}

        # 2. 确定 rule_list
        if rule_list is not None:
            unknown = [rid for rid in rule_list if rid not in RULE_REGISTRY]
            if unknown:
                return {"passed": False, "violations": [], "error": f"未知的 rule_id: {', '.join(unknown)}"}
            target_ids = [rid for rid in rule_list if rid in self.checker_ids]
        else:
            target_ids = self.checker_ids

        # 3. check
        ctx = CheckContext(raw_sql=sql, statements=statements)
        results: list[dict] = []
        for rule_id in target_ids:
            checker = RULE_REGISTRY[rule_id]()
            try:
                for v in checker.check(ctx):
                    results.append({"rule": rule_id, "message": v.message, "severity": v.severity})
            except Exception:
                logger.exception("Checker %s 执行异常", rule_id)

        # 4. result
        return {"passed": len(results) == 0, "violations": results}
