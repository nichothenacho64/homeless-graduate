from __future__ import annotations

from typing import Optional

from src.preparation.abs import clean_abs_display_text, parse_abs_number


def format_abs_column_label(value: object) -> Optional[str]:
    text = clean_abs_display_text(value)
    if text is None:
        return None

    parts = [part.strip() for part in text.split("|") if part.strip()]
    if not parts:
        return None

    return parts[-1]


def parse_abs_year(value: object) -> Optional[int]:
    parsed_year = parse_abs_number(value)
    if parsed_year is None:
        return None

    return int(parsed_year)
