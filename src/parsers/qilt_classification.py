from __future__ import annotations

import re

import pandas as pd

from src.types import QILTTableKind
from src.parsers.sheets import UNNAMED_HEADER_LABEL

YEAR_PATTERN = re.compile(r"\b20\d{2}\b")

SINGLE_METRIC_EXPECTED_ROW_COUNT = 1
METRIC_ROWS_MAX_ROW_COUNT = 5

QILT_PARTICIPATING_INSTITIONS_LINE = "No. of participating institutions"


def classify_qilt_table(table: pd.DataFrame) -> QILTTableKind:
    column_names = [str(column) for column in table.columns]
    data_columns = [column for column in column_names if not column.startswith(UNNAMED_HEADER_LABEL + "_")]

    row_count = len(table)

    year_column_flags = [_looks_like_year_column(column) for column in data_columns]

    all_data_columns_are_years = all(year_column_flags)
    any_data_column_is_year = any(year_column_flags)

    if any(QILT_PARTICIPATING_INSTITIONS_LINE in column for column in column_names):
        return "collection_summary"

    if _column_contains_value(table, "Original Study Level"):
        return "transition_matrix"

    if row_count == SINGLE_METRIC_EXPECTED_ROW_COUNT and all_data_columns_are_years:
        return "single_metric_time_series"

    if row_count <= METRIC_ROWS_MAX_ROW_COUNT and all_data_columns_are_years:
        return "metric_rows"

    if any_data_column_is_year:
        return "wide_multi_year"

    return "wide_table"

def _column_contains_value(table: pd.DataFrame, target: str) -> bool:
    for column in table.columns:
        values = table[column].dropna().astype(str).str.strip()
        if (values == target).any():
            return True

    return False

def _looks_like_year_column(column_name: str) -> bool:
    return YEAR_PATTERN.search(column_name) is not None
