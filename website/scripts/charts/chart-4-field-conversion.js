import { loadChartData } from "../data.js";
import {
    createChart4GainLegend,
    createEqualityLineTrace,
    getFieldConversionColour,
} from "../chart-helpers.js";
import { renderChart } from "../rendering.js";

export async function renderChart4(chartId) {
    const { chartData, chartMetadata } = await loadChartData(chartId);
    const metadataMetricLabels = chartMetadata.labels.metrics;

    const xKey = "short_term_fte_pct";
    const yKey = "medium_term_fte_pct";

    const xLabel = metadataMetricLabels[xKey].label;
    const yLabel = metadataMetricLabels[yKey].label;

    const data = [];
    const equalityLineTrace = createEqualityLineTrace(50, 100);
    const gainLegendTraces = createChart4GainLegend();
    
    equalityLineTrace.showlegend = false;
    
    data.push(equalityLineTrace);

    for (let gainLegendTrace of gainLegendTraces) {
        data.push(gainLegendTrace);
    }

    for (let row of chartData) {
        console.log(row);
        const employmentGain = row["medium_term_fte_pct"] - row["short_term_fte_pct"];

        const trace = {
            x: [row[xKey]],
            y: [row[yKey]],
            name: row["study_area"],
            mode: "markers",
            type: "scatter",
            showlegend: false,
            marker: {
                size: 8,
                color: getFieldConversionColour(row),
            },
            hovertemplate: `<b>%{fullData.name}</b><br>` +
                `${xLabel}: %{x}%<br>` +
                `${yLabel}: %{y}%<br>` +
                `${"Change"}: ${employmentGain.toFixed(1)} pp` +
                `<extra></extra>`,
            hoverlabel: {
                font: { color: "#FFF" },
            }
        };

        data.push(trace);
    }

    const layout = {
        title: { text: "Chart 4" },
        showlegend: true,
        legend: {
            title: { text: "Medium-term gain over short-term FTE" },
            traceorder: "normal"
        },
        xaxis: {
            title: { text: xLabel + " (%)" },
            range: [55, 100],
        },
        yaxis: {
            title: { text: yLabel + " (%)" },
            range: [55, 100],
        },
    };

    renderChart(chartId, data, layout);
}
