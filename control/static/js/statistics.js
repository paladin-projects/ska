document.addEventListener('DOMContentLoaded', function() {

    // Получение элемента canvas для графика
    const chartCanvas = document.getElementById('departmentsChart');
    if (!chartCanvas) {
        console.error('Element departmentsChart not found!');
        return;
    }

    // Получение данных из data-атрибутов
    const labels = JSON.parse(chartCanvas.dataset.labels || '[]');
    const values = JSON.parse(chartCanvas.dataset.values || '[]');

    // Создание графика
    const ctx = chartCanvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Количество сотрудников',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
});