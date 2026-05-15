from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from src.charts.constants import (
    AXIS_GRID_LINEWIDTH,
    CHART_2_GAP_LABEL_OFFSET,
    CHART_2_TITLE,
    CHART_2_X_AXIS,
    CONNECTOR_COLOR,
    DUMBBELL_CONNECTOR_ZORDER,
    DUMBBELL_LEFT_POINT_ZORDER,
    DUMBBELL_RIGHT_POINT_ZORDER,
    GRID_COLOR,
    SHORT_TERM_COLOR,
    SUBGROUP_CHART_TITLE_FONT_SIZE,
    TEXT_COLOR,
)
from src.charts.style import (
    add_figure_legend,
    apply_chart_style,
    draw_figure,
    draw_group_pair_y_labels,
)


def create_chart_2(chart_table: pd.DataFrame) -> Figure:
    apply_chart_style()
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
        color=CONNECTOR_COLOR,
        linewidth=2.3,
        zorder=DUMBBELL_CONNECTOR_ZORDER,
    )
    axis.scatter(
        lower_values[available_mask],
        row_positions[available_mask],
        color=SHORT_TERM_COLOR,
        s=42,
        label="Lower subgroup",
        zorder=DUMBBELL_LEFT_POINT_ZORDER,
    )
    axis.scatter(
        higher_values[available_mask],
        row_positions[available_mask],
        facecolors="white",
        edgecolors=SHORT_TERM_COLOR,
        linewidths=1.4,
        s=42,
        label="Higher subgroup",
        zorder=DUMBBELL_RIGHT_POINT_ZORDER,
    )

    for row_index in np.flatnonzero(available_mask.to_numpy()):
        axis.text(
            min(
                higher_values.iloc[row_index] + CHART_2_GAP_LABEL_OFFSET,
                CHART_2_X_AXIS.maximum - 0.4,
            ),
            row_positions[row_index],
            f"{gap_values.iloc[row_index]:.1f} pp",
            fontsize=8,
            color=TEXT_COLOR,
            ha="left",
            va="center",
        )

    _draw_pair_y_labels(axis, row_positions, ordered_table)
    axis.set_title(
        CHART_2_TITLE,
        loc="left",
        fontsize=SUBGROUP_CHART_TITLE_FONT_SIZE,
        color=TEXT_COLOR,
    )
    axis.set_xlabel("2024 short-term full-time employment (%)")
    axis.set_xlim(*CHART_2_X_AXIS.limits)
    axis.set_xticks(CHART_2_X_AXIS.ticks)
    axis.grid(
        axis="x",
        color=GRID_COLOR,
        linewidth=AXIS_GRID_LINEWIDTH,
    )
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(colors=TEXT_COLOR)
    axis.invert_yaxis()

    add_figure_legend(figure, axis, anchor=(0.98, 0.98))
    figure.tight_layout(rect=(0, 0, 1, 0.92))
    return draw_figure(figure)


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
    draw_group_pair_y_labels(
        axis,
        row_positions,
        ordered_table["subgroup_dimension"],
        pair_labels,
    )
