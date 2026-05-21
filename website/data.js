export function loadChartData(path, chartCreator) {
    d3.csv(path).then((data) => {
        chartCreator(data);
    });
}