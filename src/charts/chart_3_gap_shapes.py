from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

import src.charts.constants as ChartConstants
import src.charts.style as ChartStyle
from src.transform.constants import MEDIUM_TERM_TIME_WINDOW, SHORT_TERM_TIME_WINDOW


def create_chart_3(chart_table: pd.DataFrame) -> Figure:
    ChartStyle.apply_chart_style()
    ordered_table = chart_table.sort_values(
        ["sort_order", "time_window_order"],
        kind="mergesort",
    ).reset_index(drop=True)
    wide_table = ordered_table.pivot(
        index=["sort_order", "comparison_id", "subgroup_dimension"],
        columns="time_window",
        values="gap_pp",
    ).reset_index()
    wide_table = wide_table.sort_values(
        ["sort_order", "subgroup_dimension"],
        kind="mergesort",
    ).reset_index(drop=True)
    row_positions = np.arange(len(wide_table))

    short_gaps = pd.to_numeric(wide_table[SHORT_TERM_TIME_WINDOW], errors="coerce")
    medium_gaps = pd.to_numeric(wide_table[MEDIUM_TERM_TIME_WINDOW], errors="coerce")
    available_mask = short_gaps.notna() & medium_gaps.notna()

    figure, axis = plt.subplots(figsize=(8.2, 5.2))
    axis.hlines(
        row_positions[available_mask],
        short_gaps[available_mask],
        medium_gaps[available_mask],
        color=ChartConstants.CONNECTOR_COLOR,
        linewidth=2.2,
        zorder=ChartConstants.DUMBBELL_CONNECTOR_ZORDER,
    )
    axis.scatter(
        short_gaps[available_mask],
        row_positions[available_mask],
        color=ChartConstants.SHORT_TERM_COLOR,
        s=44,
        label=ChartConstants.CATCH_UP_SHORT_TERM_LABEL,
        zorder=ChartConstants.DUMBBELL_LEFT_POINT_ZORDER,
    )
    axis.scatter(
        medium_gaps[available_mask],
        row_positions[available_mask],
        color=ChartConstants.MEDIUM_TERM_COLOR,
        edgecolors="white",
        linewidths=0.9,
        s=44,
        label=ChartConstants.CATCH_UP_MEDIUM_TERM_LABEL,
        zorder=ChartConstants.DUMBBELL_RIGHT_POINT_ZORDER,
    )

    axis.set_yticks(row_positions, wide_table["subgroup_dimension"])
    axis.tick_params(axis="y", left=False)
    axis.set_title(
        ChartConstants.CHART_3_TITLE,
        loc="left",
        fontsize=ChartConstants.SUBGROUP_CHART_TITLE_FONT_SIZE,
        color=ChartConstants.TEXT_COLOR,
    )
    axis.set_xlabel("Full-time employment gap width (percentage points)")
    axis.set_xlim(*ChartConstants.CHART_3_X_AXIS.limits)
    axis.set_xticks(ChartConstants.CHART_3_X_AXIS.ticks)
    axis.grid(
        axis="x",
        color=ChartConstants.GRID_COLOR,
        linewidth=ChartConstants.AXIS_GRID_LINEWIDTH,
    )
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(colors=ChartConstants.TEXT_COLOR)
    axis.invert_yaxis()

    ChartStyle.add_figure_legend(figure, axis, anchor=(0.98, 0.98))
    figure.tight_layout(rect=(0, 0, 1, 0.92))
    return ChartStyle.draw_figure(figure)
