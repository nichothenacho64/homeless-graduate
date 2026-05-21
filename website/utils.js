export function transformValue(value) {
    if (typeof value !== "string") return value;

    if (value.trim() === "") return value;

    const numericValue = Number(value.trim());
    if (Number.isFinite(numericValue)) return numericValue;

    return value;
}

export function formatPercentage(value) {
    return Number.isFinite(value) ? `${value}%` : value;
}

export function unpack(data, key) {
    return data.map(row => row[key]);
}

export function capitaliseWord(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
}

export function createChartElementId(chartId) {
    let splitChartId = chartId.split("_");
    console.log(splitChartId);
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