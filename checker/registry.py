from __future__ import annotations

from checker.base import BaseChecker
from checker.no_count_distinct import NoCountDistinctChecker
from checker.no_count_star import NoCountStarChecker
from checker.no_distinct import NoDistinctChecker
from checker.no_right_join import NoRightJoinChecker
from checker.require_partition import RequirePartitionFilterChecker
from checker.subquery_alias import SubqueryAliasChecker
from checker.field_alias import FieldAliasChecker

RULE_REGISTRY: dict[str, type[BaseChecker]] = {
    "SQL-DISTINCT-001": NoDistinctChecker,
    "SQL-COUNT-001": NoCountStarChecker,
    "SQL-COUNT-DISTINCT-001": NoCountDistinctChecker,
    "SQL-PARTITION-001": RequirePartitionFilterChecker,
    "SQL-JOIN-RIGHT-001": NoRightJoinChecker,
    "SQL-SUBQUERY-ALIAS-001": SubqueryAliasChecker,
    "SQL-FIELD-ALIAS-001": FieldAliasChecker,
}
