from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Violation:
    message: str
    severity: str = "error"


@dataclass
class CheckContext:
    raw_sql: str
    statements: list = field(default_factory=list)


class BaseChecker(ABC):
    rule_id: str  # 每个checker必须声明自己的rule_id

    @abstractmethod
    def check(self, ctx: CheckContext) -> list[Violation]:
        ...
