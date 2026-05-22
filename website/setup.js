import { CHART_1_ID, CHART_METADATA_ID, DATA_DIR, GLOBAL_CONFIG } from "./config.js";
import {
    capitaliseWord,
    transformValue,
    formatPercentage,
    unpack
} from "./utils.js";

export function addFonts(layout) { // could later become an add defaults function
    const fontFamily = '"Source Sans 3", sans-serif';

    return {
        ...layout,
        font: {
            ...layout.font,
            family: fontFamily
        },
        hoverlabel: {
            ...layout.hoverlabel,
            font: {
                ...layout.hoverlabel?.font, // optional chaining is neeeded here to prevent accessing .font on undefined
                family: fontFamily
            }
        }
    };
}

export function createChartElementId(chartId) {
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

export async function loadChartData(chartId) {
    const metadataPath = DATA_DIR + CHART_METADATA_ID + ".json";
    const chartMetadata = await d3.json(metadataPath).then(metadata => metadata[chartId]);
    const dataPath = DATA_DIR + chartId + ".csv";
    const chartData = await d3.csv(dataPath).then(data => data);

    return { chartData, chartMetadata };
}

export function transformChartData(chartData) {
    let transformedChartData = [];

    for (let row of chartData) {
        Object.entries(row).forEach(([columnName, value]) => {
            row[columnName] = transformValue(value);
        });

        transformedChartData.push(row);
    }

    return transformedChartData;
}

export function getTrace(rows, traceKey, targetTraceOrderValue) {
    const trace = [];

    for (let row of rows) {
        const traceOrderValue = row[traceKey];
        if (traceOrderValue === targetTraceOrderValue) {
            trace.push(row);
        }
    }

    return trace;
}

export function getAxisValues(chartTrace, axisKey) {
    const axisValues = [];

    for (let row of chartTrace) {
        const axisValue = row[axisKey];
        axisValues.push(axisValue);
    }

    return axisValues;
}

export function getSeriesValue(chartTrace, seriesKeyLabel, metadataLabels) {
    const seriesKey = chartTrace[0][seriesKeyLabel];
    const seriesValue = metadataLabels[seriesKey];

    return seriesValue;
}

export function renderChart(chartId, data, layout) {
    const chartElementId = createChartElementId(chartId);
    const renderedLayout = addFonts(layout);
    return Plotly.newPlot(chartElementId, data, renderedLayout, GLOBAL_CONFIG);
}