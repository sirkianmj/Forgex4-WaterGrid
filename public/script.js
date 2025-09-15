document.addEventListener('DOMContentLoaded', () => {
    const simulationForm = document.getElementById('simulation-form');
    const locationInput = document.getElementById('location');
    const surfaceAreaInput = document.getElementById('surface-area');
    const resultDisplay = document.getElementById('result-display');
    const chartDisplay = document.getElementById('chart-display');

    simulationForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const location = locationInput.value;
        const surfaceArea = parseFloat(surfaceAreaInput.value);
        showLoadingState();

        try {
            const response = await fetch('/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ surface_area: surfaceArea, location: location }),
            });
            
            // This line is important to handle non-JSON error responses
            if (!response.ok) {
                // If we get here, it's a 500 or 404 error, etc.
                const errorText = await response.text();
                throw new Error(errorText || `An error occurred (Status: ${response.status})`);
            }

            const result = await response.json();
            showSuccessState(result);

        } catch (error) {
            console.error('Fetch or JSON Parse Error:', error);
            showErrorState('Could not process the simulation server response. The server may be down or returning an invalid format.');
        }
    });

    function showLoadingState() {
        resultDisplay.innerHTML = `<div class="spinner-border text-light" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Fetching real-world weather and running simulation...</p>`;
        chartDisplay.innerHTML = '';
    }

    function showErrorState(errorMessage) {
        resultDisplay.innerHTML = `<div class="alert alert-danger" role="alert"><h4 class="alert-heading">Simulation Failed</h4><p>${errorMessage}</p></div>`;
    }

    function showSuccessState(data) {
        const yieldValue = data.estimated_yield_liters_per_day;
        const humidity = (data.live_weather_data.relative_humidity * 100).toFixed(0);
        const temp = data.live_weather_data.temperature_celsius.toFixed(1);

        resultDisplay.innerHTML = `
            <h3 class="display-4">${yieldValue} L/day</h3>
            <p class="lead">Estimated daily water yield for <strong>${data.input_parameters.location}</strong>.</p>
            <p class="text-muted">Based on live weather: ${humidity}% humidity at ${temp}°C.</p>
        `;

        // --- THIS IS THE FINAL, CORRECTED LOGIC ---
        // I have removed the bug. This will now work correctly.
        if (data.anomaly_flag === true) {
            const warningHTML = `
                <div class="alert alert-warning mt-3" role="alert">
                    <strong>Warning:</strong> This result is statistically anomalous and may indicate a data error or system malfunction.
                </div>
            `;
            resultDisplay.insertAdjacentHTML('beforeend', warningHTML);
        }

        renderForecastChart(data.forecast_7_day);
    }

    function renderForecastChart(forecastData) {
        const trace = {
            x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            y: forecastData,
            type: 'bar',
            marker: { color: '#ffffff' },
        };
        const layout = {
            title: { text: 'Projected Yield (Liters)', font: { color: '#ffffff' } },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            xaxis: { gridcolor: '#333333' },
            yaxis: { gridcolor: '#333333' }
        };
        Plotly.newPlot('chart-display', [trace], layout, { responsive: true });
    }
});