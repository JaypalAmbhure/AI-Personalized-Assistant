// Chart.js Configuration and Dynamic Loading for Dashboard
document.addEventListener('DOMContentLoaded', function () {
    const trendCtx = document.getElementById('trendChart');
    const categoryCtx = document.getElementById('categoryChart');
    const needsWantsCtx = document.getElementById('needsWantsChart');

    if (!trendCtx && !categoryCtx && !needsWantsCtx) {
        return; // Not on dashboard page
    }

    const month = new URLSearchParams(window.location.search).get('month') || '';
    const year = new URLSearchParams(window.location.search).get('year') || '';

    fetch(`/api/chart-data?month=${month}&year=${year}`)
        .then(response => response.json())
        .then(data => {
            // Chart defaults for Dark Mode
            Chart.defaults.color = '#94a3b8';
            Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

            // 1. Trend Chart (6 Months Inflow vs Outflow)
            if (trendCtx && data.trends) {
                new Chart(trendCtx, {
                    type: 'bar',
                    data: {
                        labels: data.trends.labels,
                        datasets: [
                            {
                                label: 'Income',
                                data: data.trends.incomes,
                                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                                borderRadius: 6,
                                barThickness: 16
                            },
                            {
                                label: 'Expenses',
                                data: data.trends.expenses,
                                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                                borderRadius: 6,
                                barThickness: 16
                            },
                            {
                                label: 'Net Savings',
                                data: data.trends.savings,
                                type: 'line',
                                borderColor: '#6366f1',
                                borderWidth: 3,
                                pointBackgroundColor: '#6366f1',
                                pointRadius: 4,
                                tension: 0.35,
                                fill: false
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: { boxWidth: 12, padding: 15 }
                            },
                            tooltip: {
                                padding: 12,
                                boxPadding: 6,
                                cornerRadius: 8
                            }
                        },
                        scales: {
                            x: {
                                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                                ticks: { color: '#94a3b8' }
                            },
                            y: {
                                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                                ticks: { color: '#94a3b8' }
                            }
                        }
                    }
                });
            }

            // 2. Category Donut Chart
            if (categoryCtx && data.categories) {
                if (data.categories.labels.length === 0) {
                    categoryCtx.parentElement.innerHTML = `
                        <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted py-5">
                            <i class="fa-solid fa-chart-pie fa-3x mb-3 opacity-25"></i>
                            <p class="mb-0">No expenses recorded for this month</p>
                        </div>
                    `;
                } else {
                    new Chart(categoryCtx, {
                        type: 'doughnut',
                        data: {
                            labels: data.categories.labels,
                            datasets: [{
                                data: data.categories.values,
                                backgroundColor: data.categories.colors,
                                borderWidth: 0,
                                hoverOffset: 8
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            cutout: '72%',
                            plugins: {
                                legend: {
                                    position: 'bottom',
                                    labels: {
                                        boxWidth: 10,
                                        padding: 12,
                                        color: '#cbd5e1'
                                    }
                                }
                            }
                        }
                    });
                }
            }

            // 3. Needs vs Wants Chart
            if (needsWantsCtx && data.needs_wants) {
                new Chart(needsWantsCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.needs_wants.labels,
                        datasets: [{
                            data: data.needs_wants.values,
                            backgroundColor: data.needs_wants.colors,
                            borderWidth: 0,
                            hoverOffset: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '75%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { boxWidth: 10, padding: 10, color: '#cbd5e1' }
                            }
                        }
                    }
                });
            }
        })
        .catch(err => console.error("Error fetching financial chart data:", err));
});
