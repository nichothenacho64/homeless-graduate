export const DATA_DIR = "../data/processed/";

const REMOVED_MODE_BAR_BUTTONS = [
    "select2d", "lasso2d",
    "zoomIn2d", "zoomOut2d",
    "autoScale2d",
    "hoverCompareCartesian", "hoverClosestCartesian",
    "toggleSpikelines"
];

const TO_IMAGE_BUTTON_OPTIONS = { format: "png" };

export const CHART_1_ID = "chart_1_transition_window";
export const CHART_2_ID = "chart_2_subgroup_bottleneck";
export const CHART_3_ID = "chart_3_gap_shapes";
export const CHART_4_ID = "chart_4_field_conversion";
export const CHART_5_ID = "chart_5_work_fit";
export const CHART_6A_ID = "chart_6a_skill_by_age";
export const CHART_6B_ID = "chart_6b_degree_supply";
export const CHART_7_ID = "chart_7_subgroup_comparator";
export const CHART_METADATA_ID = "chart_metadata";

export const GLOBAL_CONFIG = {
    responsive: true,
    displayModeBar: "hover",
    displaylogo: false,
    modeBarButtonsToRemove: REMOVED_MODE_BAR_BUTTONS,
    toImageButtonOptions: TO_IMAGE_BUTTON_OPTIONS
};