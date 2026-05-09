from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import src.charts.constants as ChartConstants
import src.charts.style as ChartStyle


def create_chart_2(chart_table: pd.DataFrame) -> Figure:
    ChartStyle.apply_chart_style()
    ordered_table = chart_table.sort_values(
        ["sort_order", "subgroup_dimension"],
        kind="mergesort",
    ).reset_index(drop=True)
    row_positions = np.arange(len(ordered_table))

    lower_values = pd.to_numeric(ordered_table["lower_group_pct"], errors="coerce")
    higher_values = pd.to_numeric(ordered_table["higher_group_pct"], errors="coerce")
    gap_values = pd.to_numeric(ordered_table["gap_pp"], errors="coerce")
    available_mask = lower_values.notna() & higher_values.notna()

    figure, axis = plt.subplots(figsize=(8.2, 5.4))
    axis.hlines(
        row_positions[available_mask],
        lower_values[available_mask],
        higher_values[available_mask],
        color=ChartConstants.CONNECTOR_COLOR,
        linewidth=2.3,
        zorder=ChartConstants.DUMBBELL_CONNECTOR_ZORDER,
    )
    axis.scatter(
        lower_values[available_mask],
        row_positions[available_mask],
        color=ChartConstants.SHORT_TERM_COLOR,
        s=42,
        label="Lower subgroup",
        zorder=ChartConstants.DUMBBELL_LEFT_POINT_ZORDER,
    )
    axis.scatter(
        higher_values[available_mask],
        row_positions[available_mask],
        facecolors="white",
        edgecolors=ChartConstants.SHORT_TERM_COLOR,
        linewidths=1.4,
        s=42,
        label="Higher subgroup",
        zorder=ChartConstants.DUMBBELL_RIGHT_POINT_ZORDER,
    )

    for row_index in np.flatnonzero(available_mask.to_numpy()):
        axis.text(
            min(
                higher_values.iloc[row_index] + ChartConstants.CHART_2_GAP_LABEL_OFFSET,
                ChartConstants.CHART_2_X_AXIS.maximum - 0.4,
            ),
            row_positions[row_index],
            f"{gap_values.iloc[row_index]:.1f} pp",
            fontsize=8,
            color=ChartConstants.TEXT_COLOR,
            ha="left",
            va="center",
        )

    _draw_pair_y_labels(axis, row_positions, ordered_table)
    axis.set_title(
        ChartConstants.CHART_2_TITLE,
        loc="left",
        fontsize=ChartConstants.SUBGROUP_CHART_TITLE_FONT_SIZE,
        color=ChartConstants.TEXT_COLOR,
    )
    axis.set_xlabel("2024 short-term full-time employment (%)")
    axis.set_xlim(*ChartConstants.CHART_2_X_AXIS.limits)
    axis.set_xticks(ChartConstants.CHART_2_X_AXIS.ticks)
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


def _draw_pair_y_labels(
    axis: Axes,
    row_positions: np.ndarray,
    ordered_table: pd.DataFrame,
) -> None:
    pair_labels = [
        f"{lower} vs {higher}"
        for lower, higher in zip(
            ordered_table["lower_group"],
            ordered_table["higher_group"],
        )
    ]
    ChartStyle.draw_group_pair_y_labels(
        axis,
        row_positions,
        ordered_table["subgroup_dimension"],
        pair_labels,
    )
