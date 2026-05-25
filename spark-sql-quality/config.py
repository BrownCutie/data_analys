from __future__ import annotations

from pathlib import Path

import yaml

_RULES_FILE = Path(__file__).parent / "rules.yaml"


def load_enabled_rules() -> list[str]:
    with open(_RULES_FILE) as f:
        cfg = yaml.safe_load(f)
    if isinstance(cfg, list):
        return cfg
    return cfg.get("enabled", [])
