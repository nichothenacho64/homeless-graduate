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
