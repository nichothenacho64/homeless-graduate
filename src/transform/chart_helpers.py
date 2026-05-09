from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def select_chart_table_schema(
    table: pd.DataFrame,
    columns: Sequence[str],
) -> pd.DataFrame:
    expected_columns = list(columns)
    missing_columns = [
        column for column in expected_columns if column not in table.columns
    ]
    extra_columns = [
        column for column in table.columns if column not in expected_columns
    ]

    if missing_columns or extra_columns:
        message_parts: list[str] = []
        if missing_columns:
            message_parts.append(f"missing columns: {missing_columns}")
        if extra_columns:
            message_parts.append(f"unexpected columns: {extra_columns}")

        raise ValueError("Chart table schema mismatch; " + "; ".join(message_parts))

    return table.loc[:, expected_columns].reset_index(drop=True)
