import {
    getAxisValues,
    getSeriesValue,
    getTrace,
    loadChartData,
} from "../data.js";
import { renderChart } from "../rendering.js";
import {
    CHART_2_TRACE_COLOURS,
    CHART_AXES,
    CHART_TITLES,
} from "../config.js";

// chart 2: gradually built up from basic examples featured here: https://plotly.com/javascript/line-charts/

export async function renderChart2(chartId) {
    const { chartData, chartMetadata } = await loadChartData(chartId);
    const metadataSeriesLabels = chartMetadata.labels.series;

    const data = [];

    for (let seriesOrder = 0; seriesOrder < 3; seriesOrder++) {
        const chartTrace = getTrace(chartData, "series_order", seriesOrder);
        const seriesValue = getSeriesValue(chartTrace, "series_key", metadataSeriesLabels);

        const trace = {
            x: getAxisValues(chartTrace, "display_year"),
            y: getAxisValues(chartTrace, "value_pct"),
            name: seriesValue,
            type: "scatter",
            mode: "lines+markers",
            marker: {
                color: CHART_2_TRACE_COLOURS[seriesOrder],
            },
            hovertemplate: `${CHART_AXES.chart2XAxis}: %{x}<br>` +
                `${CHART_AXES.chart2YAxis}: %{y}%` +
                `<extra></extra>`
        };

        data.push(trace);
    }

    const layout = {
        title: { text: CHART_TITLES.chart2 },
        xaxis: {
            title: { text: CHART_AXES.chart2XAxis },
            showgrid: false,
            dtick: 1, // the increment step
        },
        yaxis: {
            title: { text: CHART_AXES.chart2YAxis + " (%)" },
            showline: false,
            range: [69, 96]
        },
    };

    renderChart(chartId, data, layout);
}
