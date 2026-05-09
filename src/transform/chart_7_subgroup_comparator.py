from __future__ import annotations

import re
from typing import Optional

import pandas as pd

from src.preparation.qilt import clean_qilt_display_text, normalise_qilt_key_text
from src.transform.chart_helpers import select_chart_table_schema
from src.transform.constants import (
    CHART_7_TABLE_COLUMNS,
    CHART_7_HIGHER_GROUP_ROLE,
    CHART_7_LOWER_GROUP_ROLE,
    GOS_8_SOURCE_KEY,
    GOS_L_160_SOURCE_KEY,
    GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS,
    GOS_SHORT_TERM_COMPARISON_COLUMNS,
    MEDIUM_TERM_TIME_WINDOW,
    SHORT_TERM_TIME_WINDOW,
    TOTAL_ROW_GROUP,
)
from src.transform.qilt import (
    format_qilt_subgroup_label,
    make_qilt_subgroup_key,
    select_qilt_ordered_pair_rows,
)
from src.types import QILTPreparedSheet


def build_chart_7_table(
    gos_sheet: QILTPreparedSheet,
    gos_l_sheet: QILTPreparedSheet,
) -> pd.DataFrame:
    comparison_table = _build_subgroup_comparison_table(
        gos_sheet.table,
        gos_l_sheet.table,
    )
    summary_rows = [
        _build_comparator_rows(group_table)
        for _, group_table in comparison_table.groupby("subgroup_dimension", sort=False)
    ]
    chart_table = pd.DataFrame(row for group_rows in summary_rows for row in group_rows)
    chart_table["sort_order"] = _build_sort_order(chart_table)
    chart_table["_group_role_order"] = chart_table["group_role"].map(
        {
            CHART_7_LOWER_GROUP_ROLE: 0,
            CHART_7_HIGHER_GROUP_ROLE: 1,
        }
    )
    chart_table = chart_table.sort_values(
        ["sort_order", "time_window_order", "_group_role_order"],
        kind="mergesort",
    ).drop(columns="_group_role_order")
    return select_chart_table_schema(chart_table, CHART_7_TABLE_COLUMNS)


def _build_subgroup_comparison_table(
    gos_table: pd.DataFrame,
    gos_l_table: pd.DataFrame,
) -> pd.DataFrame:
    short_table = _normalise_short_term_table(gos_table)
    medium_table = _normalise_medium_term_table(gos_l_table)
    return short_table.merge(
        medium_table,
        on="subgroup_key",
        how="inner",
        sort=False,
        validate="one_to_one",
    )


def _normalise_short_term_table(gos_table: pd.DataFrame) -> pd.DataFrame:
    prepared_rows: list[dict[str, object]] = []

    for _, row in gos_table.iterrows():
        row_group = clean_qilt_display_text(row["row_group"])
        row_label = clean_qilt_display_text(row["row_label"])

        if row_group is None or row_group == TOTAL_ROW_GROUP:
            continue

        prepared_rows.append(
            {
                "subgroup_dimension": row_group,
                "row_label": row_label,
                "subgroup_key": make_qilt_subgroup_key(row_group, row_label),
                "short_term_value_pct": row[
                    GOS_SHORT_TERM_COMPARISON_COLUMNS[
                        "short_term_full_time_employment"
                    ]
                ],
            }
        )

    return pd.DataFrame(prepared_rows)


def _normalise_medium_term_table(gos_l_table: pd.DataFrame) -> pd.DataFrame:
    prepared_rows: list[dict[str, object]] = []

    for _, row in gos_l_table.iterrows():
        row_group = clean_qilt_display_text(row["row_group"])
        row_label = clean_qilt_display_text(row["row_label"])

        if row_group is None or row_group == TOTAL_ROW_GROUP:
            continue

        prepared_rows.append(
            {
                "subgroup_key": make_qilt_subgroup_key(row_group, row_label),
                "medium_term_value_pct": row[
                    GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS[
                        "medium_term_full_time_employment"
                    ]
                ],
            }
        )

    return pd.DataFrame(prepared_rows)


def _build_comparator_rows(group_table: pd.DataFrame) -> list[dict[str, object]]:
    subgroup_dimension = str(group_table["subgroup_dimension"].iloc[0])
    selector_id = _build_selector_id(subgroup_dimension)
    selected_pair = select_qilt_ordered_pair_rows(
        group_table.rename(columns={"subgroup_dimension": "row_group"}),
        value_column="short_term_value_pct",
    )

    if selected_pair is None:
        return []

    low_row, high_row = selected_pair
    return [
        *_build_group_rows(
            low_row,
            selector_id=selector_id,
            selector_label=subgroup_dimension,
            group_role=CHART_7_LOWER_GROUP_ROLE,
        ),
        *_build_group_rows(
            high_row,
            selector_id=selector_id,
            selector_label=subgroup_dimension,
            group_role=CHART_7_HIGHER_GROUP_ROLE,
        ),
    ]


def _build_group_rows(
    row: pd.Series,
    *,
    selector_id: str,
    selector_label: str,
    group_role: str,
) -> list[dict[str, object]]:
    group_label = format_qilt_subgroup_label(row["row_label"])
    return [
        {
            "selector_id": selector_id,
            "selector_label": selector_label,
            "subgroup_dimension": selector_label,
            "group_role": group_role,
            "group_label": group_label,
            "time_window": SHORT_TERM_TIME_WINDOW,
            "time_window_order": 0,
            "value_pct": row["short_term_value_pct"],
            "source_key": GOS_8_SOURCE_KEY,
        },
        {
            "selector_id": selector_id,
            "selector_label": selector_label,
            "subgroup_dimension": selector_label,
            "group_role": group_role,
            "group_label": group_label,
            "time_window": MEDIUM_TERM_TIME_WINDOW,
            "time_window_order": 1,
            "value_pct": row["medium_term_value_pct"],
            "source_key": GOS_L_160_SOURCE_KEY,
        },
    ]


def _build_selector_id(subgroup_dimension: object) -> str:
    key_text = normalise_qilt_key_text(subgroup_dimension)
    if key_text is None:
        return "unknown"

    return re.sub(r"[^a-z0-9]+", "_", key_text).strip("_")


def _build_sort_order(chart_table: pd.DataFrame) -> pd.Series:
    short_term_rows = chart_table.loc[
        chart_table["time_window"] == SHORT_TERM_TIME_WINDOW,
        ["subgroup_dimension", "group_role", "value_pct"],
    ]
    gap_rows: list[dict[str, object]] = []

    for subgroup_dimension, group_table in short_term_rows.groupby(
        "subgroup_dimension",
        sort=False,
    ):
        low_value = _select_role_value(group_table, CHART_7_LOWER_GROUP_ROLE)
        high_value = _select_role_value(group_table, CHART_7_HIGHER_GROUP_ROLE)
        gap = (
            high_value - low_value
            if low_value is not None and high_value is not None
            else None
        )
        gap_rows.append({"subgroup_dimension": subgroup_dimension, "gap_pp": gap})

    ordered_dimensions = (
        pd.DataFrame(gap_rows)
        .sort_values(
            ["gap_pp", "subgroup_dimension"],
            ascending=[False, True],
            kind="mergesort",
            na_position="last",
        )["subgroup_dimension"]
        .tolist()
    )
    order_lookup = {
        subgroup_dimension: order
        for order, subgroup_dimension in enumerate(ordered_dimensions)
    }
    return chart_table["subgroup_dimension"].map(order_lookup).astype("Int64")


def _select_role_value(
    group_table: pd.DataFrame,
    group_role: str,
) -> Optional[float]:
    role_rows = group_table.loc[group_table["group_role"] == group_role]
    if role_rows.empty:
        return None

    value = role_rows["value_pct"].iloc[0]
    if pd.isna(value):
        return None

    return float(value)
