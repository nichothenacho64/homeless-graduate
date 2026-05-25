import { THEME_COLOURS } from "../config.js";
import {
    getAxisLabel,
    getAxisValues,
    loadChartData,
} from "../data.js";
import { renderChart } from "../rendering.js";

export async function renderChart6b(chartId) {
    const { chartData, chartMetadata } = await loadChartData(chartId);

    const xKey = "year";
    const yKey = "bachelor_degree_or_above_holders_increase_pct";

    const baselineYear = chartData[0][xKey];
    const yValues = getAxisValues(chartData, yKey);

    const finalRow = chartData[chartData.length - 1];

    const yLabel = getAxisLabel(chartMetadata, yKey);
    const yAxisTitle = getAxisLabel(chartMetadata, yKey, true);

    const data = [];

    const lineTrace = {
        x: getAxisValues(chartData, xKey),
        y: yValues,
        type: "scatter",
        mode: "lines+markers",
        showlegend: false,
        fill: "tozeroy", // 0.05 to hex = 12.75 (round to 13), which is D in hex (add the 0)
        fillcolor: THEME_COLOURS.amber500 + "0D", 
        line: {
            color: THEME_COLOURS.amber500,
            width: 2
        },
        marker: {
            size: 8,
            color: THEME_COLOURS.amber500,
        },
        hovertemplate: `Year: %{x}<br>` +
            `Increase since 2016: %{y:.1f}%` +
            `<extra></extra>`
    };

    const finalPointTrace = {
        x: [finalRow[xKey]],
        y: [finalRow[yKey]],
        type: "scatter",
        mode: "markers",
        showlegend: false,
        marker: {
            size: 10,
            color: THEME_COLOURS.amber700,
        },
        hovertemplate: `Year: %{x}<br>` +
            `Increase since 2016: %{y:.1f}%` +
            `<extra></extra>`
    };

    data.push(lineTrace, finalPointTrace);

    const layout = {
        title: { text: "Chart 6b" },
        xaxis: {
            title: { text: "Year" },
            range: [2016, 2025.1],
            nticks: 12,
            zeroline: false
        },
        yaxis: {
            title: { text: yAxisTitle },
            range: [0, 51],
            zeroline: false
        },
    };

    renderChart(chartId, data, layout);
}
