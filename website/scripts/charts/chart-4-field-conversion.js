import { BEST_FIT_LINE } from "../config.js";
import { getAxisValues, loadChartData } from "../data.js";
import { createBestFitLineTrace, getFieldConversionColour, getFieldConversionOpacity, renderChart } from "../rendering.js";

export async function renderChart4(chartId) {
    const { chartData, chartMetadata } = await loadChartData(chartId);
    const metadataMetricLabels = chartMetadata.labels.metrics;

    const xKey = "short_term_fte_pct";
    const yKey = "medium_term_fte_pct";

    const xLabel = metadataMetricLabels[xKey].label;
    const yLabel = metadataMetricLabels[yKey].label;

    const data = [];
    const bestFitLineTrace = createBestFitLineTrace(chartData, xKey, yKey);

    if (bestFitLineTrace) {
        data.push(bestFitLineTrace);
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
            marker: {
                size: 8,
                opacity: getFieldConversionOpacity(row),
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
        showlegend: false, // true by default
        xaxis: {
            title: { text: xLabel + " (%)" },
            range: [50, 101]
        },
        yaxis: {
            title: { text: yLabel + " (%)" },
            range: [50, 101]
        },
    };

    renderChart(chartId, data, layout);
}
