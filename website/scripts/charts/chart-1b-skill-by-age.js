import {
    getAxisLabel,
    getTrace,
    loadChartData,
} from "../data.js";
import {
    CHART_1B_TRACE_COLOURS,
    CHART_TITLES
} from "../config.js";
import { renderChart } from "../rendering.js";
import { unpack } from "../utils.js";

export async function renderChart1b(chartId) {
    const { chartData, chartMetadata } = await loadChartData(chartId);

    const data = [];

    for (let seriesOrder = 0; seriesOrder < 5; seriesOrder++) {
        const chartTrace = getTrace(chartData, "skill_order", seriesOrder);
        const traceName = chartTrace[0]["skill_level"];

        const trace = {
            x: unpack(chartTrace, "age_group"),
            y: unpack(chartTrace, "share_pct"),
            name: traceName,
            type: "bar",
            marker: {
                color: CHART_1B_TRACE_COLOURS[seriesOrder],
            },
            hovertemplate: `<b>%{fullData.name}</b><br>` +
                `Age group: %{x}<br>` +
                `Share percentage: %{y}%<br>` +
                `<extra></extra>`,
        };

        data.push(trace);
    }

    const layout = {
        title: { text: CHART_TITLES.chart1b },
        showlegend: true,
        legend: {
            title: { text: "Skill levels" },
        },
        barmode: "stack",
        xaxis: {
            title: { text: "Age group" },
        },
        yaxis: {
            title: { text: getAxisLabel(chartMetadata, "share_pct", true) },
        },
    };

    renderChart(chartId, data, layout);
}
