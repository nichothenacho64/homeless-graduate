import { BEST_FIT_LINE, GLOBAL_TRACES, GLOBAL_CONFIG, GLOBAL_LAYOUT, THEME_COLOURS } from "./config.js";
import { capitaliseWord, getMean, getBestFitNumerator, getBestFitDenominator } from "./utils.js";
import { getAxisValues, getChartPoints } from "./data.js";

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

export function createZeroLine(lineColour, lineWidth) {
    return {
        type: "line",
        layer: "below",
        x0: 0,
        x1: 0,
        y0: 0,
        y1: 1,
        xref: "x",
        yref: "paper",
        line: {
            color: lineColour,
            width: lineWidth
        }
    };
}

export function createBestFitLineTrace(chartData, xKey, yKey) {
    const xValues = getAxisValues(chartData, xKey);
    const yValues = getAxisValues(chartData, yKey);
    const chartPoints = getChartPoints(chartData, xKey, yKey);

    const xMean = getMean(xValues);
    const yMean = getMean(yValues);

    const slopeNumerator = getBestFitNumerator(chartPoints, xMean, yMean);
    const slopeDenominator = getBestFitDenominator(chartPoints, xMean);

    const slope = slopeNumerator / slopeDenominator;
    const intercept = yMean - (slope * xMean);

    const xStart = Math.min(...xValues);
    const xEnd = Math.max(...xValues);
    const yStart = (slope * xStart) + intercept;
    const yEnd = (slope * xEnd) + intercept;

    return {
        x: [xStart, xEnd],
        y: [yStart, yEnd],
        name: "Line of best fit",
        mode: "lines",
        type: "scatter",
        line: BEST_FIT_LINE,
        hoverinfo: "skip"
    };
}

export function getFieldConversionColour(row) {
    const gain = row["medium_term_fte_pct"] - row["short_term_fte_pct"];

    if (gain >= 25) {
        return THEME_COLOURS.amber700;
    }

    if (gain >= 15) {
        return THEME_COLOURS.amber500;
    }

    if (gain >= 8) {
        return THEME_COLOURS.blue500;
    }

    return THEME_COLOURS.blue700;
}

export function getFieldConversionOpacity(row) {
    const gain = row["medium_term_fte_pct"] - row["short_term_fte_pct"];

    if (gain >= 20) {
        return 1;
    }

    return 0.2;
}

export function getChartHeight(baseHeight, numRows, rowHeight) {
    return baseHeight + (numRows * rowHeight);
}

export function renderChart(chartId, data, layout) {
    const chartElementId = getChartElementId(chartId);
    const renderedData = addGlobalTraceDefaults(data);
    const renderedLayout = addGlobalLayoutDefaults(layout);
    return Plotly.newPlot(chartElementId, renderedData, renderedLayout, GLOBAL_CONFIG);
}
