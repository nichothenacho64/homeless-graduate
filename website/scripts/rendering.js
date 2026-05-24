import {
    GLOBAL_TRACES,
    GLOBAL_CONFIG,
    GLOBAL_LAYOUT
} from "./config.js";
import { capitaliseWord } from "./utils.js";

export function addGlobalLayoutDefaults(layout) {
    const fontFamily = '"Source Sans 3", sans-serif';

    return {
        ...GLOBAL_LAYOUT,
        ...layout,
        font: {
            ...layout.font,
            family: fontFamily
        },
        hoverlabel: {
            ...layout.hoverlabel,
            font: {
                ...layout.hoverlabel?.font,
                family: fontFamily
            }
        }
    };
}

function applyMarkerDefaults(marker) {
    if (!marker?.color) {
        return marker;
    }

    return {
        ...GLOBAL_TRACES.marker,
        ...marker,
        line: {
            ...GLOBAL_TRACES.marker.line,
            color: marker.color,
            ...marker.line
        }
    };
}

function applyHoverlabelDefaults(hoverlabel, traceColour) {
    return {
        ...GLOBAL_TRACES.hoverlabel,
        ...(traceColour ? { bordercolor: traceColour } : {}),
        ...hoverlabel,
        font: {
            ...GLOBAL_TRACES.hoverlabel.font,
            ...hoverlabel?.font
        }
    };
}

export function addGlobalTraceDefaults(data) {
    return data.map((trace) => {
        const marker = applyMarkerDefaults(trace.marker);
        const traceColour = marker?.line?.color ?? marker?.color ?? trace.line?.color;

        return {
            ...trace,
            ...(marker ? { marker } : {}),
            hoverlabel: applyHoverlabelDefaults(trace.hoverlabel, traceColour)
        };
    });
}

export function getChartElementId(chartId) {
    let splitChartId = chartId.split("_");
    let chartElementId;

    for (let i = 0; i < splitChartId.length; i++) {
        if (i !== 0) {
            chartElementId += capitaliseWord(splitChartId[i]);
        } else {
            chartElementId = splitChartId[i];
        }
    }

    return chartElementId;
}

export function renderChart(chartId, data, layout) {
    const chartElementId = getChartElementId(chartId);
    const renderedData = addGlobalTraceDefaults(data);
    const renderedLayout = addGlobalLayoutDefaults(layout);
    return Plotly.newPlot(chartElementId, renderedData, renderedLayout, GLOBAL_CONFIG);
}
