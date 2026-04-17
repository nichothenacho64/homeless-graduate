from src.preparation.series import series_is_numeric_like
from src.preparation.qilt import parse_qilt_number

import pandas as pd

def find_qilt_value_columns(table: pd.DataFrame) -> list[str]:
    value_columns: list[str] = []

    for column in table.columns:
        series = table[column]

        if series_is_numeric_like(series, number_parser=parse_qilt_number):
            value_columns.append(str(column))

    return value_columns

def find_qilt_label_only_rows(table: pd.DataFrame) -> pd.DataFrame:
    value_columns = find_qilt_value_columns(table)
    if not value_columns:
        return table.iloc[0:0].copy()

    non_value_columns = [column for column in table.columns if column not in value_columns]
    if not non_value_columns:
        return table.iloc[0:0].copy()

    label_only_mask = (
        table[value_columns].isna().all(axis=1)
        & table[non_value_columns].notna().any(axis=1)
    )

    return table.loc[label_only_mask].copy()

def validate_qilt_label_only_rows(table: pd.DataFrame) -> None:
    label_only_rows = find_qilt_label_only_rows(table)
    if label_only_rows.empty:
        return

    preview_rows = label_only_rows.head(5)
    preview_text = preview_rows.astype("string").fillna("").agg(" | ".join, axis=1).tolist()
    joined_preview = "; ".join(preview_text)

    raise ValueError(
        "Found QILT rows with labels but no value columns. "
        f"Examples: {joined_preview}"
    )