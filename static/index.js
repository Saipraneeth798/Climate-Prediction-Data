document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('myForm');
    const resultElement = document.getElementById('result');

    form.addEventListener('submit', async (event) => {
    event.preventDefault();  // Prevent default form submission

    // Prepare form data
    const formData = new FormData(form);
    resultElement.innerHTML = "<p>Loading...</p>"; // Show loading message

    try {
        // Send the form data to the server
        const response = await fetch('/submitform', {
            method: 'POST',
            body: formData,
        });

        // Check if the response is OK (status in the range 200-299)
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }

        // Parse the JSON response
        const result = await response.json();

        // Check if there was an error
        if (result.error) {
            resultElement.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
        } else if (result.data.length === 0) {
            resultElement.innerHTML = "<p>No data found for the given date.</p>";
        } else {
            // Display the filtered data in a nicer format
            let output = "<h3>Data:</h3><ul>";
            result.data.forEach(item => {
                output += `<li>${JSON.stringify(item)}</li>`;
            });
            output += "</ul>";
            resultElement.innerHTML = output;
        }
    } catch (error) {
        resultElement.innerHTML = `<p style="color: red;">There was an error: ${error.message}</p>`;
    }
});

        }
    });
});

