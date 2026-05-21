const DATA_DIR = "assets/data/processed/";

const REMOVED_MODE_BAR_BUTTONS = [
    "select2d", "lasso2d",
    "zoomIn2d", "zoomOut2d",
    "autoScale2d",
    "hoverCompareCartesian", "hoverClosestCartesian",
    "toggleSpikelines"
]

export const DATA_PATHS = {
    chart_1: DATA_DIR + "chart_1_transition_window.csv",
    chart_2: DATA_DIR + "chart_2_subgroup_bottleneck.csv",
    chart_3: DATA_DIR + "chart_3_gap_shapes.csv",
    chart_4: DATA_DIR + "chart_4_field_conversion.csv",
    chart_5: DATA_DIR + "chart_5_work_fit.csv",
    chart_6a: DATA_DIR + "chart_6a_skill_by_age.csv",
    chart_6b: DATA_DIR + "chart_6b_degree_supply.csv",
    chart_7: DATA_DIR + "chart_7_subgroup_comparator.csv",
    metadata: DATA_DIR + "chart_metadata.json"
};

export const GLOBAL_CONFIG = {
    responsive: true,
    displayModeBar: "hover",
    displaylogo: false,
    modeBarButtonsToRemove: REMOVED_MODE_BAR_BUTTONS,
    toImageButtonOptions: { format: "png" }
};