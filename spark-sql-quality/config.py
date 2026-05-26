from __future__ import annotations

from pathlib import Path

import yaml

_RULES_FILE = Path(__file__).parent / "rules.yaml"


def load_disabled_rules() -> list[str]:
    """读取禁用的规则列表（黑名单），未列出的规则全部执行"""
    with open(_RULES_FILE) as f:
        cfg = yaml.safe_load(f)
    if not cfg:
        return []
    return cfg.get("disabled", [])
