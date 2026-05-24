import {
    CHART_4_GAINS,
    DIAGONAL_LINE,
    THEME_COLOURS
} from "./config.js";
import { getAxisValues, getChartPoints } from "./data.js";
import { getMean, getBestFitNumerator, getBestFitDenominator } from "./utils.js";

export function createAxisMarker(row, traceNumber, groupColumn, colour) {
    const group = row[groupColumn];
    const groupPercentage = row[groupColumn + "_pct"];

    return {
        x: [groupPercentage],
        y: [traceNumber],
        mode: "markers",
        marker: {
            size: 10,
            color: colour
        },
        hovertemplate: `${row["subgroup_dimension"]}: ${group}<br>` +
            `Full-time employment: %{x}%` +
            `<extra></extra>`,
        hoverlabel: {
            font: { color: "#FFF" },
            bordercolor: colour,
        }
    };
}

export function createHollowAxisMarker(row, traceNumber, groupColumn, colour) {
    const axisMarker = createAxisMarker(row, traceNumber, groupColumn, colour);

    axisMarker.marker.color = "#FFF";
    axisMarker.hoverlabel.font.color = "#000";
    axisMarker.marker.line = {
        color: colour,
        width: 2
    };

    return axisMarker;
}

export function getComparisonLabel(row) {
    return row["reference_group"] + " vs " + row["comparison_group"];
}

export function createGapMarker(row, traceNumber, colour) {
    const comparisonLabel = getComparisonLabel(row);

    return {
        x: [row["signed_gap_pp"]],
        y: [traceNumber],
        mode: "markers",
        marker: {
            size: 10,
            color: colour
        },
        hovertemplate: `<b>${row["subgroup_dimension"]} gap: %{x} pp</b><br>` +
            `${row["reference_group"]}: ${row["reference_group_pct"]}%<br>` +
            `${row["comparison_group"]}: ${row["comparison_group_pct"]}%<br>` +
            `<extra></extra>`,
        hoverlabel: {
            font: { color: "#FFF" },
            bordercolor: colour,
        }
    };
}

export function getGapShapeYTickLabels(chartData) {
    const yTickLabels = [];

    for (let row of chartData) {
        const yTickLabel = `<b>${row["subgroup_dimension"]}</b><br>${getComparisonLabel(row)}`;
        yTickLabels.push(yTickLabel);
    }

    return yTickLabels;
}

export function addDumbbellChartLegend(marker, name, group, showLegend) {
    marker.name = name;
    marker.legendgroup = group;
    marker.showlegend = showLegend;

    return marker;
}

export function getYTickValues(chartData) {
    const yTickValues = [];

    for (let row of chartData) {
        const yTickValue = chartData.length - row["sort_order"];
        yTickValues.push(yTickValue);
    }

    return yTickValues;
}

export function getYTickLabels(chartData) {
    const yTickLabels = [];

    for (let row of chartData) {
        const subgroupComparison = row["lower_group"] + " vs " + row["higher_group"];
        const yTickLabel = `<b>${row["subgroup_dimension"]}</b><br>${subgroupComparison}`;
        yTickLabels.push(yTickLabel);
    }

    return yTickLabels;
}

export function getGapLabelAnnotations(chartData) {
    const gapLabelAnnotations = [];

    for (let row of chartData) {
        const traceNumber = chartData.length - row["sort_order"];
        const gapAnnotation = row["gap_pp"] + " pp";

        const gapLabelAnnotation = {
            x: row["higher_group_pct"],
            y: traceNumber,
            text: gapAnnotation,
            xanchor: "left",
            xshift: 12,
            yanchor: "middle",
            showarrow: false
        };

        gapLabelAnnotations.push(gapLabelAnnotation);
    }

    return gapLabelAnnotations;
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

export function createEqualityLineTrace(xStart, xEnd) {
    return {
        x: [xStart, xEnd],
        y: [xStart, xEnd],
        name: "y = x",
        mode: "lines",
        type: "scatter",
        line: DIAGONAL_LINE,
        hoverinfo: "skip"
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
        line: DIAGONAL_LINE,
        hoverinfo: "skip"
    };
}

export function getFieldConversionColour(row) {
    const gain = row["medium_term_fte_pct"] - row["short_term_fte_pct"];

    if (gain >= CHART_4_GAINS.high) {
        return THEME_COLOURS.amber700;
    }

    if (gain >= CHART_4_GAINS.medium) {
        return THEME_COLOURS.amber500;
    }

    if (gain >= CHART_4_GAINS.low) {
        return THEME_COLOURS.blue500;
    }

    return THEME_COLOURS.blue700;
}

export function getFieldConversionOpacity(row) {
    const gain = row["medium_term_fte_pct"] - row["short_term_fte_pct"];

    if (gain >= CHART_4_GAINS.high) {
        return 1;
    }

    return 0.2;
}

export function getChartHeight(baseHeight, numRows, rowHeight) {
    return baseHeight + (numRows * rowHeight);
}

export function createChart4GainLegendTrace(name, gainPp) {
    const legendRow = {
        short_term_fte_pct: 0,
        medium_term_fte_pct: gainPp
    };

    return {
        x: [null],
        y: [null],
        name,
        mode: "markers",
        type: "scatter",
        marker: {
            size: 8,
            color: getFieldConversionColour(legendRow)
        },
        hoverinfo: "skip",
        showlegend: true
    };
}

export function createChart4GainLegend() {
    const gain4Trace = createChart4GainLegendTrace(`${CHART_4_GAINS.high}+ pp`, CHART_4_GAINS.high);
    const gain3Trace = createChart4GainLegendTrace(`${CHART_4_GAINS.medium}-${CHART_4_GAINS.high - 1} pp`, CHART_4_GAINS.medium);
    const gain2Trace = createChart4GainLegendTrace(`${CHART_4_GAINS.low}-${CHART_4_GAINS.medium - 1} pp`, CHART_4_GAINS.low);
    const gain1Trace = createChart4GainLegendTrace(`<${CHART_4_GAINS.low} pp`, CHART_4_GAINS.low - 1);

    return [gain4Trace, gain3Trace, gain2Trace, gain1Trace];
}
