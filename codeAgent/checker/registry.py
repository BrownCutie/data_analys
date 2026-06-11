"""
自动扫描 registry — 递归扫描 checker/hard 和 checker/convention 下所有 .py 文件，
找到 BaseChecker 子类，用它们的 rule_id 构建映射。
新增规则只需写 .py 文件，不用改这个文件。
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from checker.base import BaseChecker

_CHECKER_ROOT = Path(__file__).parent


def _discover_checkers() -> dict[str, type[BaseChecker]]:
    """递归扫描 hard/ 和 convention/ 下所有 .py，找到 BaseChecker 子类"""
    registry: dict[str, type[BaseChecker]] = {}
    for subdir in ("hard", "convention"):
        search_dir = _CHECKER_ROOT / subdir
        if not search_dir.exists():
            continue
        for py_file in sorted(search_dir.rglob("*.py")):
            if py_file.name.startswith("_"):
                continue
            rel_path = py_file.relative_to(_CHECKER_ROOT.parent).with_suffix("")
            module_name = ".".join(rel_path.parts)
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            for _name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseChecker) and obj is not BaseChecker:
                    rule_id = getattr(obj, "rule_id", None)
                    if rule_id:
                        registry[rule_id] = obj
    return registry


# 启动时自动构建
RULE_REGISTRY: dict[str, type[BaseChecker]] = _discover_checkers()
