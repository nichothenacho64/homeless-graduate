from __future__ import annotations

from typing import Optional

import pandas as pd

from src.constants.parsing import SHEET_WHITESPACE_PATTERN
from src.exceptions import RequiredColumnsMissingError
from src.preparation.series import is_missing_value
from src.constants.qilt import (
    QILT_FOOTNOTE_SYMBOL_PATTERN,
    QILT_SUBGROUP_TEXT_EQUIVALENTS,
)


def validate_required_columns(
    table: pd.DataFrame,
    *,
    table_name: str,
    required_columns: list[str],
) -> None:
    missing_columns = [column_name for column_name in required_columns if column_name not in table.columns]
    if missing_columns:
        raise RequiredColumnsMissingError(table_name, missing_columns)


def find_unmatched_subgroup_rows(
    source_table: pd.DataFrame,
    comparison_table: pd.DataFrame,
) -> pd.DataFrame:
    source_keys = source_table[["row_group", "row_label", "subgroup_key"]].copy()
    comparison_keys = comparison_table[["subgroup_key"]].drop_duplicates()

    merged_keys = source_keys.merge(
        comparison_keys,
        on="subgroup_key",
        how="left",
        indicator=True,
    )

    unmatched_rows = merged_keys.loc[
        merged_keys["_merge"] == "left_only",
        ["row_group", "row_label"],
    ].copy()

    return unmatched_rows.reset_index(drop=True)


def format_unmatched_subgroup_rows(unmatched_rows: pd.DataFrame) -> str:
    preview_parts: list[str] = []

    for _, row in unmatched_rows.head(5).iterrows():
        row_group = str(row["row_group"])
        row_label = str(row["row_label"])
        preview_parts.append(f"{row_group} | {row_label}")

    return ", ".join(preview_parts)


def clean_qilt_display_text(value: object) -> Optional[str]:
    if is_missing_value(value):
        return None

    text = str(value).strip()
    text = QILT_FOOTNOTE_SYMBOL_PATTERN.sub("", text)
    text = SHEET_WHITESPACE_PATTERN.sub(" ", text).strip()
    return text or None


def normalise_qilt_key_text(value: object) -> Optional[str]:
    text = clean_qilt_display_text(value)
    if text is None:
        return None

    equivalent_text = QILT_SUBGROUP_TEXT_EQUIVALENTS.get(text, text)
    return equivalent_text.lower()
