from __future__ import annotations

import pandas as pd

from dataclasses import replace
from typing import Optional

from src.exceptions import EmptyTableError
from src.parsers.qilt import QILTParsedSheet, parse_qilt_sheet
from src.preparation.cleaners import (
    clean_column_name,
    clean_metadata_sections,
    clean_text,
    clean_text_value,
)
from src.preparation.numbers import parse_sheet_number
from src.preparation.series import (
    coerce_numeric_series,
    series_is_numeric_like,
    series_is_text_like,
)
from src.constants.qilt import QILT_MISSING_TEXT_VALUES, QILT_TRAILING_FOOTNOTE_PATTERN
from src.types import Folder

def prepare_qilt_sheet(folder: Folder, file_name: str, sheet_name: str) -> QILTParsedSheet:
    parsed_sheet = parse_qilt_sheet(folder, file_name, sheet_name)
    return clean_qilt_parsed_sheet(parsed_sheet)

def clean_qilt_parsed_sheet(parsed_sheet: QILTParsedSheet) -> QILTParsedSheet:
    cleaned_metadata = clean_metadata_sections(parsed_sheet.metadata, text_cleaner=_clean_qilt_text)
    cleaned_table = clean_qilt_table(parsed_sheet.table)
    return replace(
        parsed_sheet,
        table=cleaned_table,
        metadata=cleaned_metadata
    )

def clean_qilt_table(table: pd.DataFrame) -> pd.DataFrame:
    cleaned_table = table.copy()
    cleaned_columns: list[str] = []
    
    for column in cleaned_table.columns:
        cleaned_column = clean_column_name(column, text_cleaner=_clean_qilt_text)
        cleaned_columns.append(cleaned_column)

    cleaned_table.columns = cleaned_columns

    for column_name in cleaned_table.columns:
        cleaned_table[column_name] = _clean_qilt_series(cleaned_table[column_name], column_name=column_name)

    cleaned_table = cleaned_table.dropna(axis=0, how="all").dropna(axis=1, how="all")
    cleaned_table = cleaned_table.reset_index(drop=True)
    
    if cleaned_table.empty:
        raise EmptyTableError("The cleaned QILT table")

    return cleaned_table

def _clean_qilt_series(series: pd.Series, *, column_name: str) -> pd.Series:
    cleaned_series = series.map(
        lambda value: clean_text_value(value, text_cleaner=_clean_qilt_text)
    )

    if series_is_numeric_like(cleaned_series, number_parser=parse_qilt_number):
        return coerce_numeric_series(
            cleaned_series,
            column_name=column_name,
            number_parser=parse_qilt_number,
        )

    if series_is_text_like(cleaned_series):
        return cleaned_series.astype("string")

    return cleaned_series

def _clean_qilt_text(value: object) -> Optional[str]:
    return clean_text(value, missing_text_values=QILT_MISSING_TEXT_VALUES)

def parse_qilt_number(value: object) -> Optional[int | float]:
    return parse_sheet_number(
        value,
        trailing_note_pattern=QILT_TRAILING_FOOTNOTE_PATTERN,
    )
