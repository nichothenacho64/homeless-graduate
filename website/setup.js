import { CHART_3_ID, CHART_METADATA_ID, DATA_DIR, GLOBAL_CONFIG } from "./config.js";
import { transformValue, formatPercentage, createChartElementId } from "./utils.js";

export function addFonts(layout) {
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

export async function loadChartData(chartId) {
    const metadataPath = DATA_DIR + CHART_METADATA_ID + ".json";
    const chartMetadata = await d3.json(metadataPath).then(metadata => metadata[chartId]);
    const dataPath = DATA_DIR + chartId + ".csv";
    const chartData = await d3.csv(dataPath).then(data => data);

    return { chartData, chartMetadata };
}

export function transformChartData(chartData) {
    let transformedRows = [];

    for (let row of chartData) {
        Object.entries(row).forEach(([columnName, value]) => {
            row[columnName] = transformValue(value);
        });

        transformedRows.push(row);
    }

    return transformedRows;
}

// function 

function renderChart(chartId, data, layout) {
    const chartElementId = createChartElementId(chartId);
    const renderedLayout = addFonts(layout);
    return Plotly.newPlot(chartElementId, data, renderedLayout, GLOBAL_CONFIG);
}

const { chartData, chartMetadata } = await loadChartData(CHART_3_ID);
const transformedChartData = transformChartData(chartData);
console.log(transformedChartData);
