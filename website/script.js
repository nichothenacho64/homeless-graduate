import {
    loadChartData,
    transformChartData,
    getSeriesValue,
    getTrace,
    getAxisValues,
    renderChart
} from "./setup.js";
import { CHART_1_ID } from "./config.js";

async function renderChart1() {
    const { chartData, chartMetadata } = await loadChartData(CHART_1_ID);
    const transformedChartData = transformChartData(chartData);
    const metadataSeriesLabels = chartMetadata.labels.series;

    const data = [];

    for (let seriesOrder = 0; seriesOrder < 3; seriesOrder++) {
        const chartTrace = getTrace(transformedChartData, "series_order", seriesOrder);
        const seriesValue = getSeriesValue(chartTrace, "series_key", metadataSeriesLabels);

        const trace = {
            x: getAxisValues(chartTrace, "display_year"),
            y: getAxisValues(chartTrace, "value_pct"),
            mode: "lines+markers",
            name: seriesValue,
            type: "scatter"
        };

        data.push(trace);
    }

    // gradually built up from basic examples features here: https://plotly.com/javascript/line-charts/
    const layout = {
        title: { text: "Chart 1" },
        showlegend: true, // false by default
        xaxis: {
            title: {
                text: 'Graduation year'
            },
            showgrid: false,
            zeroline: false
        },
        yaxis: {
            title: {
                text: 'Full-time employment (%)'
            },
            showline: false
        }
    };

    renderChart(CHART_1_ID, data, layout);
}

await renderChart1();