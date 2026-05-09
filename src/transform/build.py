from __future__ import annotations

from collections.abc import Mapping

from src.loaders import initialise_abs_sheet, initialise_gos_l_sheet, initialise_gos_sheet
from src.preparation.abs import prepare_abs_sheet
from src.preparation.qilt import prepare_qilt_sheet
from src.transform.chart_1_transition_window import build_chart_1_table
from src.transform.chart_2_subgroup_bottleneck import build_chart_2_table
from src.transform.chart_3_gap_shapes import build_chart_3_table
from src.transform.chart_4_field_conversion import build_chart_4_table
from src.transform.chart_5_work_fit import build_chart_5_table
from src.transform.chart_6a_sew_skill_by_age import build_chart_6a_table
from src.transform.chart_6b_sew_degree_supply import build_chart_6b_table
from src.transform.chart_7_subgroup_comparator import build_chart_7_table
from src.transform.constants import (
    CHART_1_ID,
    CHART_2_ID,
    CHART_3_ID,
    CHART_4_ID,
    CHART_5_ID,
    CHART_6A_ID,
    CHART_6B_ID,
    CHART_7_ID,
    GOS_5_SOURCE_KEY,
    GOS_8_SOURCE_KEY,
    GOS_21_SOURCE_KEY,
    GOS_L_1_SOURCE_KEY,
    GOS_L_6_SOURCE_KEY,
    GOS_L_26_SOURCE_KEY,
    GOS_L_160_SOURCE_KEY,
    SEW_32_SOURCE_KEY,
    SEW_35_SOURCE_KEY,
)
from src.types import ExcelSheet, PreparedSheet, SheetPreparer


def prepare_sheets(
    sheet_specs: Mapping[str, ExcelSheet],
    prepare_sheet: SheetPreparer,
) -> dict[str, PreparedSheet]:
    return {
        source_key: prepare_sheet(sheet.folder, sheet.file_name, sheet.sheet_name)
        for source_key, sheet in sheet_specs.items()
    }


qilt_sheet_specs = {
    GOS_21_SOURCE_KEY: initialise_gos_sheet(21),
    GOS_5_SOURCE_KEY: initialise_gos_sheet(5),
    GOS_8_SOURCE_KEY: initialise_gos_sheet(8),
    GOS_L_1_SOURCE_KEY: initialise_gos_l_sheet(1),
    GOS_L_6_SOURCE_KEY: initialise_gos_l_sheet(6),
    GOS_L_26_SOURCE_KEY: initialise_gos_l_sheet(26),
    GOS_L_160_SOURCE_KEY: initialise_gos_l_sheet(160),
}
abs_sheet_specs = {
    SEW_32_SOURCE_KEY: initialise_abs_sheet(32),
    SEW_35_SOURCE_KEY: initialise_abs_sheet(35),
}

prepared_qilt_sheets = prepare_sheets(qilt_sheet_specs, prepare_qilt_sheet)
prepared_abs_sheets = prepare_sheets(abs_sheet_specs, prepare_abs_sheet)
chart_sources = {**prepared_qilt_sheets, **prepared_abs_sheets}

chart_tables = {
    CHART_1_ID: build_chart_1_table(
        prepared_qilt_sheets[GOS_21_SOURCE_KEY],
        prepared_qilt_sheets[GOS_L_1_SOURCE_KEY],
    ),
    CHART_2_ID: build_chart_2_table(
        prepared_qilt_sheets[GOS_8_SOURCE_KEY],
        prepared_qilt_sheets[GOS_5_SOURCE_KEY],
    ),
    CHART_3_ID: build_chart_3_table(
        prepared_qilt_sheets[GOS_8_SOURCE_KEY],
        prepared_qilt_sheets[GOS_L_160_SOURCE_KEY],
    ),
    CHART_4_ID: build_chart_4_table(
        prepared_qilt_sheets[GOS_L_6_SOURCE_KEY],
    ),
    CHART_5_ID: build_chart_5_table(
        prepared_qilt_sheets[GOS_L_6_SOURCE_KEY],
        prepared_qilt_sheets[GOS_L_26_SOURCE_KEY],
    ),
    CHART_6A_ID: build_chart_6a_table(
        prepared_abs_sheets[SEW_32_SOURCE_KEY],
    ),
    CHART_6B_ID: build_chart_6b_table(
        prepared_abs_sheets[SEW_35_SOURCE_KEY],
    ),
    CHART_7_ID: build_chart_7_table(
        prepared_qilt_sheets[GOS_8_SOURCE_KEY],
        prepared_qilt_sheets[GOS_L_160_SOURCE_KEY],
    ),
}
