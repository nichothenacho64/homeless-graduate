from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path

import pandas as pd

from src.sources import PROCESSED_DIR
from src.transform.constants import (
    CHART_METADATA_FILE_NAME,
    CHART_METADATA_SPECS,
    CHART_OUTPUT_FILENAMES,
    CHART_SOURCE_KEY_COLUMNS,
    QILT_METRIC_DEFINITIONS,
    QILT_SOURCE_METADATA_SPECS,
    SEW_RELIABILITY_MARKER_MEANINGS,
    SEW_UNIT_DEFINITIONS,
    TIME_WINDOW_DEFINITIONS,
)
from src.types import ABSPreparedSheet, QILTPreparedSheet


def export_chart_table(table: pd.DataFrame, filename: str) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / filename
    table.to_csv(path, index=False)
    return path


def export_chart_tables(chart_tables: Mapping[str, pd.DataFrame]) -> dict[str, Path]:
    exported_paths: dict[str, Path] = {}

    for chart_id, table in chart_tables.items():
        if chart_id not in CHART_OUTPUT_FILENAMES:
            raise KeyError(f"No chart output filename is defined for {chart_id!r}.")

        exported_paths[chart_id] = export_chart_table(
            table,
            CHART_OUTPUT_FILENAMES[chart_id],
        )

    return exported_paths


def export_chart_metadata_json(metadata: Mapping[str, object]) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / CHART_METADATA_FILE_NAME
    path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return path


def build_chart_metadata(
    chart_tables: Mapping[str, pd.DataFrame],
    chart_sources: Mapping[str, object],
) -> dict[str, object]:
    metadata: dict[str, object] = {}

    for chart_id, chart_table in chart_tables.items():
        if chart_id not in CHART_METADATA_SPECS:
            raise KeyError(f"No chart metadata spec is defined for {chart_id!r}.")
        if chart_id not in CHART_OUTPUT_FILENAMES:
            raise KeyError(f"No chart output filename is defined for {chart_id!r}.")

        source_keys = _collect_source_keys(chart_table)
        chart_entry: dict[str, object] = {
            "chart_id": chart_id,
            "data_file": CHART_OUTPUT_FILENAMES[chart_id],
            "source_keys": source_keys,
            "sources": _build_sources(source_keys, chart_sources),
        }
        chart_entry.update(_build_chart_spec_metadata(CHART_METADATA_SPECS[chart_id]))

        excluded_comparisons = _build_missing_gap_notes(chart_table)
        if excluded_comparisons:
            chart_entry["excluded_comparisons"] = excluded_comparisons

        metadata[chart_id] = chart_entry

    return metadata


def build_qilt_source_metadata(
    source_key: str,
    prepared_sheet: QILTPreparedSheet,
) -> dict[str, object]:
    if source_key not in QILT_SOURCE_METADATA_SPECS:
        raise KeyError(f"No QILT source metadata spec is defined for {source_key!r}.")

    source_spec = QILT_SOURCE_METADATA_SPECS[source_key]
    return {
        "source_key": source_key,
        "source_system": source_spec["source_system"],
        "dataset": source_spec["dataset"],
        "dataset_label": source_spec["dataset_label"],
        "plain_label": source_spec["plain_label"],
        "source_file": source_spec["source_file"],
        "sheet_name": prepared_sheet.sheet_name,
        "sheet_number": source_spec["sheet_number"],
        "sheet_title": prepared_sheet.title,
        "classification": prepared_sheet.classification,
        "source_metadata": prepared_sheet.metadata,
        "suppression_unavailable_note": (
            "Blank exported values reflect source values that were suppressed, "
            "unavailable, or not present after QILT preparation."
        ),
    }


def build_abs_source_metadata(
    source_key: str,
    prepared_sheet: ABSPreparedSheet,
) -> dict[str, object]:
    expected_source_key = f"sew_{prepared_sheet.table_number}"
    if source_key != expected_source_key:
        raise ValueError(
            f"SEW source key {source_key!r} does not match "
            f"table {prepared_sheet.table_number}."
        )

    return {
        "source_key": source_key,
        "source_system": "ABS",
        "dataset": "SEW",
        "dataset_label": "ABS Education and Work",
        "plain_label": f"SEW #{prepared_sheet.table_number}",
        "source_file": prepared_sheet.source_file,
        "sheet_name": prepared_sheet.sheet_name,
        "table_number": prepared_sheet.table_number,
        "sheet_title": prepared_sheet.title,
        "source_metadata": prepared_sheet.metadata,
        "units": SEW_UNIT_DEFINITIONS,
        "reliability": {
            "is_reliable": (
                "True only when the retained national/Australia-wide value has no "
                "warning marker and is not suppressed or unavailable."
            ),
            "marker_meanings": SEW_RELIABILITY_MARKER_MEANINGS,
        },
        "suppression_unavailable_note": (
            "SEW values marked *, **, #, np, or na are not reliable for chart claims."
        ),
    }


def _build_chart_spec_metadata(spec: Mapping[str, object]) -> dict[str, object]:
    spec_metadata = dict(spec)
    metric_keys = spec_metadata.get("metric_keys")
    time_windows = spec_metadata.get("time_windows")

    if isinstance(metric_keys, list):
        spec_metadata["metric_definitions"] = _select_metric_definitions(metric_keys)
    if isinstance(time_windows, list):
        spec_metadata["time_window_definitions"] = {
            time_window: TIME_WINDOW_DEFINITIONS[time_window]
            for time_window in time_windows
        }

    return spec_metadata


def _select_metric_definitions(metric_keys: list[str]) -> dict[str, str]:
    return {
        metric_key: QILT_METRIC_DEFINITIONS[metric_key]
        for metric_key in metric_keys
        if metric_key in QILT_METRIC_DEFINITIONS
    }


def _collect_source_keys(chart_table: pd.DataFrame) -> list[str]:
    source_keys: list[str] = []

    for column in CHART_SOURCE_KEY_COLUMNS:
        if column not in chart_table.columns:
            continue

        for source_key in chart_table[column].dropna().tolist():
            source_key_text = str(source_key)
            if source_key_text not in source_keys:
                source_keys.append(source_key_text)

    return source_keys


def _build_sources(
    source_keys: list[str],
    chart_sources: Mapping[str, object],
) -> dict[str, object]:
    sources: dict[str, object] = {}

    for source_key in source_keys:
        if source_key not in chart_sources:
            raise KeyError(f"Missing prepared source for chart source key {source_key!r}.")

        prepared_sheet = chart_sources[source_key]
        if isinstance(prepared_sheet, QILTPreparedSheet):
            sources[source_key] = build_qilt_source_metadata(source_key, prepared_sheet)
        elif isinstance(prepared_sheet, ABSPreparedSheet):
            sources[source_key] = build_abs_source_metadata(source_key, prepared_sheet)
        else:
            raise TypeError("Chart source metadata requires QILTPreparedSheet or ABSPreparedSheet.")

    return sources


def _build_missing_gap_notes(chart_table: pd.DataFrame) -> list[dict[str, object]]:
    if "gap_pp" not in chart_table:
        return []

    missing_rows = chart_table.loc[chart_table["gap_pp"].isna()]
    if missing_rows.empty:
        return []

    notes: list[dict[str, object]] = []
    for _, row in missing_rows.iterrows():
        note: dict[str, object] = {
            "reason": "Comparison unavailable after suppressed or missing values.",
        }
        if "subgroup_dimension" in row:
            note["subgroup_dimension"] = row["subgroup_dimension"]
        if "time_window" in row:
            note["time_window"] = row["time_window"]
        notes.append(note)

    return notes
