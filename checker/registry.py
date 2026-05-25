from __future__ import annotations

from checker.base import BaseChecker

# ── 硬性规则：命中即禁止，必须修复 ──────────────────────────────
from checker.hard.no_count_distinct import NoCountDistinctChecker
from checker.hard.no_count_star import NoCountStarChecker
from checker.hard.no_distinct import NoDistinctChecker
from checker.hard.no_implicit_join import NoImplicitJoinChecker
from checker.hard.no_right_join import NoRightJoinChecker
from checker.hard.no_select_star import NoSelectStarChecker

# ── 规范检查：必须符合约定 ────────────────────────────────────
from checker.convention.field_alias import FieldAliasChecker
from checker.convention.group_by import GroupByChecker
from checker.convention.join_filter_first import JoinFilterFirstChecker
from checker.convention.null_zero import NullZeroChecker
from checker.convention.partition_filter import PartitionFilterChecker
from checker.convention.subquery_alias import SubqueryAliasChecker
from checker.convention.table_alias import TableAliasChecker
from checker.convention.temp_table_naming import TempTableNamingChecker

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
