// Wait until the entire HTML document is loaded before running the script.
document.addEventListener('DOMContentLoaded', () => {

    // --- CONFIGURATION ---
    // IMPORTANT: Replace this with the public URL of your FastAPI backend.
    // It's the URL from the "Ports" tab in VS Code.
    const API_BASE_URL = 'https://upgraded-rotary-phone-76746x4g9vv3pxvp-8000.app.github.dev'; 

    // --- DOM ELEMENT REFERENCES ---
    const simulationForm = document.getElementById('simulation-form');
    const locationInput = document.getElementById('location');
    const surfaceAreaInput = document.getElementById('surface-area');
    const resultDisplay = document.getElementById('result-display');
    const chartDisplay = document.getElementById('chart-display');

    // --- EVENT LISTENER ---
    // This function runs when the "Run Simulation" button is clicked.
    simulationForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevents the webpage from reloading on form submission.

        // Get user input values.
        const location = locationInput.value;
        const surfaceArea = parseFloat(surfaceAreaInput.value);

        // Update the UI to show a loading state.
        showLoadingState();

        try {
            // Call our backend API.
            const response = await fetch(`${API_BASE_URL}/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    surface_area: surfaceArea,
                    location: location,
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                // If the API returns an error (like our 401 key error), display it.
                // The 'result.detail' part is specific to how FastAPI formats errors.
                showErrorState(result.detail || `An error occurred (Status: ${response.status})`);
            } else {
                // If the API call is successful, display the results.
                showSuccessState(result);
            }

        } catch (error) {
            // This catches network errors (e.g., if the backend is down).
            console.error('Fetch Error:', error);
            showErrorState('Could not connect to the simulation server.');
        }
    });

    // --- UI UPDATE FUNCTIONS ---
    function showLoadingState() {
        resultDisplay.innerHTML = `
            <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Fetching real-world weather and running simulation...</p>
        `;
        // Clear previous chart
        chartDisplay.innerHTML = '';
    }

    function showErrorState(errorMessage) {
        resultDisplay.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Simulation Failed</h4>
                <p>${errorMessage}</p>
            </div>
        `;
    }

    function showSuccessState(data) {
        // This function will be expanded in the next step to include the chart.
        const yieldValue = data.estimated_yield_liters_per_day;
        const humidity = (data.live_weather_data.relative_humidity * 100).toFixed(0);
        const temp = data.live_weather_data.temperature_celsius.toFixed(1);

        resultDisplay.innerHTML = `
            <h3 class="display-4">${yieldValue} L/day</h3>
            <p class="lead">
                Estimated daily water yield for <strong>${data.input_parameters.location}</strong>.
            </p>
            <p class="text-muted">
                Based on live weather: ${humidity}% humidity at ${temp}°C.
            </p>
        `;
    }
});