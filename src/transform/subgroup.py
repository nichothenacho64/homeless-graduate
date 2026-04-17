from __future__ import annotations

import pandas as pd

from src.exceptions import InvalidSubgroupRowError, SubgroupRowsMismatchError
from src.constants.qilt import (
    GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS,
    GOS_SHORT_TERM_COMPARISON_COLUMNS,
)
from src.transform.qilt import (
    clean_qilt_display_text,
    find_unmatched_subgroup_rows,
    format_unmatched_subgroup_rows,
    normalise_qilt_key_text,
    validate_required_columns,
)

def build_subgroup_comparison_table(
    gos_table: pd.DataFrame,
    gos_l_table: pd.DataFrame,
    *,
    include_total: bool = True,
) -> pd.DataFrame:
    prepared_gos_table = _prepare_subgroup_comparison_source(
        gos_table,
        source_name="GOS",
        metric_columns=GOS_SHORT_TERM_COMPARISON_COLUMNS,
    )
    prepared_gos_l_table = _prepare_subgroup_comparison_source(
        gos_l_table,
        source_name="GOS-L",
        metric_columns=GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS,
    )

    _validate_matching_subgroups(
        prepared_gos_table,
        prepared_gos_l_table,
        left_name="GOS",
        right_name="GOS-L",
    )

    comparison_table = prepared_gos_table.merge(
        prepared_gos_l_table[
            [
                "subgroup_key",
                *GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS.keys(),
            ]
        ],
        on="subgroup_key",
        how="inner",
        sort=False,
    )

    comparison_table["full_time_employment_change"] = (
        comparison_table["medium_term_full_time_employment"]
        - comparison_table["short_term_full_time_employment"]
    ).round(1)
    comparison_table["overall_employment_change"] = (
        comparison_table["medium_term_overall_employment"]
        - comparison_table["short_term_overall_employment"]
    ).round(1)
    comparison_table["labour_force_participation_change"] = (
        comparison_table["medium_term_labour_force_participation"]
        - comparison_table["short_term_labour_force_participation"]
    ).round(1)

    if not include_total:
        total_mask = comparison_table["subgroup_key"].map(
            lambda subgroup_key: isinstance(subgroup_key, tuple) and subgroup_key[0] == "total"
        )
        comparison_table = comparison_table.loc[~total_mask].copy()

    final_columns = [
        "row_group",
        "row_label",
        "short_term_full_time_employment",
        "medium_term_full_time_employment",
        "full_time_employment_change",
        "short_term_overall_employment",
        "medium_term_overall_employment",
        "overall_employment_change",
        "short_term_labour_force_participation",
        "medium_term_labour_force_participation",
        "labour_force_participation_change",
    ]

    return comparison_table[final_columns].reset_index(drop=True)


def build_gos_gos_l_subgroup_comparison_table(
    gos_table: pd.DataFrame,
    gos_l_table: pd.DataFrame,
    *,
    include_total: bool = True,
) -> pd.DataFrame:
    return build_subgroup_comparison_table(
        gos_table,
        gos_l_table,
        include_total=include_total,
    )


def _prepare_subgroup_comparison_source(
    table: pd.DataFrame,
    *,
    source_name: str,
    metric_columns: dict[str, str],
) -> pd.DataFrame:
    required_columns = ["row_group", "row_label", *metric_columns.values()]
    validate_required_columns(
        table,
        table_name=source_name,
        required_columns=required_columns,
    )

    prepared_rows: list[dict[str, object]] = []

    for _, row in table.iterrows():
        row_group = clean_qilt_display_text(row["row_group"])
        row_label = clean_qilt_display_text(row["row_label"])

        if row_group is None or row_label is None:
            raise InvalidSubgroupRowError(source_name, "an empty group or label")

        subgroup_key = _build_subgroup_key(row_group, row_label)
        if subgroup_key is None:
            raise InvalidSubgroupRowError(source_name, "an unusable comparison key")

        prepared_row: dict[str, object] = {
            "row_group": row_group,
            "row_label": row_label,
            "subgroup_key": subgroup_key,
        }

        for output_column, source_column in metric_columns.items():
            prepared_row[output_column] = row[source_column]

        prepared_rows.append(prepared_row)

    return pd.DataFrame(prepared_rows)


def _build_subgroup_key(row_group: str, row_label: str) -> tuple[str, str] | None:
    row_group_key = normalise_qilt_key_text(row_group)
    row_label_key = normalise_qilt_key_text(row_label)

    if row_group_key is None or row_label_key is None:
        return None

    return (row_group_key, row_label_key)


def _validate_matching_subgroups(
    left_table: pd.DataFrame,
    right_table: pd.DataFrame,
    *,
    left_name: str,
    right_name: str,
) -> None:
    unmatched_left_rows = find_unmatched_subgroup_rows(left_table, right_table)
    if not unmatched_left_rows.empty:
        preview = format_unmatched_subgroup_rows(unmatched_left_rows)
        raise SubgroupRowsMismatchError(left_name, right_name, preview)

    unmatched_right_rows = find_unmatched_subgroup_rows(right_table, left_table)
    if not unmatched_right_rows.empty:
        preview = format_unmatched_subgroup_rows(unmatched_right_rows)
        raise SubgroupRowsMismatchError(right_name, left_name, preview)
