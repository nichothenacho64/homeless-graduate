export function transformValue(value) {
    if (typeof value !== "string") return value;

    if (value.trim() === "") return value;

    const numericValue = Number(value.trim());
    if (Number.isFinite(numericValue)) return numericValue;

    return value;
}

export function capitaliseWord(word) {
    return word.charAt(0).toUpperCase() + word.slice(1);
}

export function createNumberList(value) {
    let numberArray = [];
    
    for (let i = 1; i <= value; i++) {
        numberArray.push(i);
    }
    return numberArray;
}

export function getMean(values) {
    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export function getBestFitNumerator(points, xMean, yMean) {
    return points.reduce((sum, point) => {
        return sum + ((point.x - xMean) * (point.y - yMean));
    }, 0);
}

export function getBestFitDenominator(points, xMean) {
    return points.reduce((sum, point) => {
        return sum + ((point.x - xMean) ** 2);
    }, 0);
}
