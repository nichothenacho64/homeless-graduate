from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

import src.charts.constants as ChartConstants
import src.charts.style as ChartStyle
from src.transform.constants import CHART_1_SERIES_ORDER


def create_chart_1(chart_table: pd.DataFrame) -> Figure:
    ChartStyle.apply_chart_style()
    ordered_table = chart_table.copy()
    ordered_table["series_order"] = ordered_table["series_key"].map(
        CHART_1_SERIES_ORDER
    )
    ordered_table = ordered_table.sort_values(
        ["series_order", "year"],
        kind="mergesort",
    )

    figure, axis = plt.subplots(figsize=(8.8, 4.6))

    for series_key, series_table in ordered_table.groupby("series_key", sort=False):
        axis.plot(
            series_table["year"],
            series_table["value_pct"],
            color=ChartConstants.CHART_1_SERIES_COLORS[series_key],
            linewidth=2.4,
            marker="o",
            markersize=6,
            markerfacecolor=ChartConstants.CHART_1_SERIES_MARKER_FACES[series_key],
            markeredgecolor=ChartConstants.CHART_1_SERIES_COLORS[series_key],
            markeredgewidth=1.2,
            label=ChartConstants.CHART_1_SERIES_LABELS[series_key],
        )

    axis.set_title(
        ChartConstants.CHART_1_TITLE,
        loc="left",
        fontsize=ChartConstants.SUBGROUP_CHART_TITLE_FONT_SIZE,
        color=ChartConstants.TEXT_COLOR,
    )
    axis.set_xlabel("Graduation year")
    axis.set_ylabel("Full-time employment (%)")
    axis.set_ylim(*ChartConstants.CHART_1_Y_LIMITS)
    axis.set_yticks(ChartConstants.CHART_1_Y_TICKS)
    axis.grid(
        axis="y",
        color=ChartConstants.GRID_COLOR,
        linewidth=ChartConstants.AXIS_GRID_LINEWIDTH,
    )
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(colors=ChartConstants.TEXT_COLOR)

    ChartStyle.add_figure_legend(figure, axis, anchor=(0.98, 0.98))
    figure.tight_layout(rect=(0, 0, 1, 0.92))
    return ChartStyle.draw_figure(figure)
