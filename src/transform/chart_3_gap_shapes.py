from __future__ import annotations

import re
from typing import Optional

import pandas as pd

from src.preparation.qilt import clean_qilt_display_text, normalise_qilt_key_text
from src.transform.chart_helpers import select_chart_table_schema
from src.transform.constants import (
    CHART_3_TABLE_COLUMNS,
    GOS_8_SOURCE_KEY,
    GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS,
    GOS_L_160_SOURCE_KEY,
    GOS_SHORT_TERM_COMPARISON_COLUMNS,
    MEDIUM_TERM_TIME_WINDOW,
    SHORT_TERM_TIME_WINDOW,
    TOTAL_ROW_GROUP,
)
from src.transform.qilt import make_qilt_subgroup_key, select_qilt_ordered_pair_rows
from src.types import QILTPreparedSheet


def build_chart_3_table(
    gos_sheet: QILTPreparedSheet,
    gos_l_sheet: QILTPreparedSheet,
) -> pd.DataFrame:
    comparison_table = _build_subgroup_comparison_table(
        gos_sheet.table,
        gos_l_sheet.table,
    )
    summary_rows = [
        _build_gap_shape_rows(group_table)
        for _, group_table in comparison_table.groupby("subgroup_dimension", sort=False)
    ]
    summary_table = pd.DataFrame(
        row for group_rows in summary_rows for row in group_rows
    )
    summary_table["sort_order"] = _build_sort_order(summary_table)
    chart_table = summary_table.sort_values(
        ["sort_order", "time_window_order"],
        kind="mergesort",
    ).reset_index(drop=True)
    return select_chart_table_schema(chart_table, CHART_3_TABLE_COLUMNS)


def _build_subgroup_comparison_table(
    gos_table: pd.DataFrame,
    gos_l_table: pd.DataFrame,
) -> pd.DataFrame:
    short_table = _normalise_short_term_table(gos_table)
    medium_table = _normalise_medium_term_table(gos_l_table)
    return short_table.merge(
        medium_table[
            [
                "subgroup_key",
                "medium_term_full_time_employment",
            ]
        ],
        on="subgroup_key",
        how="inner",
        sort=False,
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
                "short_term_full_time_employment": row[
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
                "medium_term_full_time_employment": row[
                    GOS_L_MEDIUM_TERM_COMPARISON_COLUMNS[
                        "medium_term_full_time_employment"
                    ]
                ],
            }
        )

    return pd.DataFrame(prepared_rows)


def _build_gap_shape_rows(group_table: pd.DataFrame) -> list[dict[str, object]]:
    subgroup_dimension = str(group_table["subgroup_dimension"].iloc[0])
    comparison_id = _build_comparison_id(subgroup_dimension)
    short_term_extremes = select_qilt_ordered_pair_rows(
        group_table.rename(columns={"subgroup_dimension": "row_group"}),
        value_column="short_term_full_time_employment",
    )
    medium_term_extremes = select_qilt_ordered_pair_rows(
        group_table.rename(columns={"subgroup_dimension": "row_group"}),
        value_column="medium_term_full_time_employment",
    )

    short_gap = _calculate_gap(short_term_extremes, "short_term_full_time_employment")
    medium_gap = _calculate_gap(medium_term_extremes, "medium_term_full_time_employment")

    return [
        {
            "comparison_id": comparison_id,
            "subgroup_dimension": subgroup_dimension,
            "time_window": SHORT_TERM_TIME_WINDOW,
            "time_window_order": 0,
            "gap_pp": short_gap,
            "source_key": GOS_8_SOURCE_KEY,
        },
        {
            "comparison_id": comparison_id,
            "subgroup_dimension": subgroup_dimension,
            "time_window": MEDIUM_TERM_TIME_WINDOW,
            "time_window_order": 1,
            "gap_pp": medium_gap,
            "source_key": GOS_L_160_SOURCE_KEY,
        },
    ]


def _calculate_gap(
    extremes: Optional[tuple[pd.Series, pd.Series]],
    value_column: str,
) -> Optional[float]:
    if extremes is None:
        return None

    low_row, high_row = extremes
    low_value = low_row[value_column]
    high_value = high_row[value_column]

    if pd.isna(low_value) or pd.isna(high_value):
        return None

    return round(float(high_value - low_value), 1)


def _build_comparison_id(subgroup_dimension: object) -> str:
    key_text = normalise_qilt_key_text(subgroup_dimension)
    if key_text is None:
        return "unknown"

    return re.sub(r"[^a-z0-9]+", "_", key_text).strip("_")


def _build_sort_order(summary_table: pd.DataFrame) -> pd.Series:
    short_term_rows = summary_table.loc[
        summary_table["time_window"] == SHORT_TERM_TIME_WINDOW,
        ["subgroup_dimension", "gap_pp"],
    ]
    ordered_dimensions = (
        short_term_rows.sort_values(
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
    return summary_table["subgroup_dimension"].map(order_lookup).astype("Int64")
