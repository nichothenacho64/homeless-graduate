from __future__ import annotations

import pandas as pd

from src.preparation.qilt import clean_qilt_display_text
from src.transform.chart_helpers import select_chart_table_schema
from src.transform.constants import (
    CHART_5_TABLE_COLUMNS,
    CHART_5_WORK_FIT_METRIC_KEY,
    GOS_L_6_SOURCE_KEY,
    GOS_L_26_SOURCE_KEY,
)
from src.types import QILTPreparedSheet


def build_chart_5_table(
    employment_sheet: QILTPreparedSheet,
    fit_sheet: QILTPreparedSheet,
) -> pd.DataFrame:
    employment_table = _normalise_employment_table(employment_sheet.table)
    fit_table = _normalise_fit_table(fit_sheet.table)
    merged_table = employment_table.merge(
        fit_table,
        on="study_area",
        how="inner",
        validate="one_to_one",
        sort=False,
    )

    merged_table["fte_gain_pp"] = (
        merged_table["medium_term_fte_pct"] - merged_table["short_term_fte_pct"]
    ).round(1)
    merged_table["fit_change_pp"] = (
        merged_table["short_term_underutilisation_pct"]
        - merged_table["medium_term_underutilisation_pct"]
    ).round(1)
    merged_table["fit_metric_key"] = CHART_5_WORK_FIT_METRIC_KEY
    merged_table["employment_source_key"] = GOS_L_6_SOURCE_KEY
    merged_table["fit_source_key"] = GOS_L_26_SOURCE_KEY

    chart_table = merged_table.loc[
        :,
        CHART_5_TABLE_COLUMNS,
    ].sort_values("study_area", kind="mergesort")
    return select_chart_table_schema(chart_table, CHART_5_TABLE_COLUMNS)


def _normalise_employment_table(table: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "study_area": table["area"].map(clean_qilt_display_text),
            "short_term_fte_pct": table["short_term_full_time_employed"],
            "medium_term_fte_pct": table["medium_term_full_time_employed"],
        }
    )


def _normalise_fit_table(table: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "study_area": table["area"].map(clean_qilt_display_text),
            "short_term_underutilisation_pct": table[
                "extent_to_which_skills_and_education_not_fully_utilised_short_term_fte"
            ],
            "medium_term_underutilisation_pct": table[
                "extent_to_which_skills_and_education_not_fully_utilised_medium_term_fte"
            ],
        }
    )
