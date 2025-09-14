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

       /* // --- TEMPORARY TEST BLOCK ---
        // Since your API key is not active, we will use mock data to test the chart.
        // Once your key is working, you can delete this block and uncomment the 'try...catch' block below.
        
        console.log("--- USING MOCK DATA FOR TESTING ---");
        const mockSuccessData = {
            "input_parameters": { "surface_area": surfaceArea, "location": location },
            "live_weather_data": { "relative_humidity": 0.45, "temperature_celsius": 28.5 },
            "estimated_yield_liters_per_day": 146.1,
            "forecast_7_day": [146.1, 153.41, 143.18, 160.71, 138.8, 149.02, 157.79]
        };
        showSuccessState(mockSuccessData);
        // --- END OF TEMPORARY TEST BLOCK ---
        */



        // --- REAL API CALL BLOCK ---
        // This is the real code. It is commented out for now.
        try {
            const response = await fetch('/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ surface_area: surfaceArea, location: location }),
            });
            const result = await response.json();
            if (!response.ok) {
                showErrorState(result.detail || `An error occurred (Status: ${response.status})`);
            } else {
                showSuccessState(result);
            }
        } catch (error) {
            console.error('Fetch Error:', error);
            showErrorState('Could not connect to the simulation server.');
        }
        // --- END OF REAL API CALL BLOCK ---
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

        // NEW: Call the function to render our chart
        renderForecastChart(data.forecast_7_day);
    }

    // NEW: Function to render the chart with Plotly.js
    function renderForecastChart(forecastData) {
        const trace = {
            x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            y: forecastData,
            type: 'bar',
            marker: {
                color: '#ffffff', // White bars
                line: {
                    color: '#000000',
                    width: 1
                }
            }
        };

        const layout = {
            title: { text: 'Projected Yield (Liters)', font: { color: '#ffffff' } },
            paper_bgcolor: 'rgba(0,0,0,0)', // Transparent background
            plot_bgcolor: 'rgba(0,0,0,0)', // Transparent plot area
            font: { color: '#ffffff' },
            xaxis: { gridcolor: '#333333' },
            yaxis: { gridcolor: '#333333' }
        };

        Plotly.newPlot('chart-display', [trace], layout, {responsive: true});
    }
});