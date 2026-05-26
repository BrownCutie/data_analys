from __future__ import annotations

from .base import BaseChecker

# ── 硬性规则：命中即禁止，必须修复 ──────────────────────────────
from .hard.no_count_distinct import NoCountDistinctChecker
from .hard.no_count_star import NoCountStarChecker
from .hard.no_distinct import NoDistinctChecker
from .hard.no_implicit_join import NoImplicitJoinChecker
from .hard.no_right_join import NoRightJoinChecker
from .hard.no_select_star import NoSelectStarChecker

# ── 规范检查：必须符合约定 ────────────────────────────────────
from .convention.field_alias import FieldAliasChecker
from .convention.group_by import GroupByChecker
from .convention.join_filter_first import JoinFilterFirstChecker
from .convention.null_zero import NullZeroChecker
from .convention.partition_filter import PartitionFilterChecker
from .convention.subquery_alias import SubqueryAliasChecker
from .convention.table_alias import TableAliasChecker
from .convention.temp_table_naming import TempTableNamingChecker

RULE_REGISTRY: dict[str, type[BaseChecker]] = {
    # ── 硬性规则 ──
    "SQL-DISTINCT-001": NoDistinctChecker,
    "SQL-COUNT-001": NoCountStarChecker,
    "SQL-COUNT-DISTINCT-001": NoCountDistinctChecker,
    "SQL-JOIN-RIGHT-001": NoRightJoinChecker,
    "SQL-JOIN-IMPLICIT-001": NoImplicitJoinChecker,
    "SQL-SELECT-STAR-001": NoSelectStarChecker,
    # ── 规范检查 ──
    "SQL-TABLE-ALIAS-001": TableAliasChecker,
    "SQL-SUBQUERY-ALIAS-001": SubqueryAliasChecker,
    "SQL-FIELD-ALIAS-001": FieldAliasChecker,
    "SQL-TEMP-TABLE-001": TempTableNamingChecker,
    "SQL-PARTITION-001": PartitionFilterChecker,
    "SQL-JOIN-FILTER-001": JoinFilterFirstChecker,
    "SQL-GROUP-BY-001": GroupByChecker,
    "SQL-NULL-ZERO-001": NullZeroChecker,
}
