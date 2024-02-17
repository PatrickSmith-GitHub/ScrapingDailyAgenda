function startScraping() {
    // Get selected school from dropdown
    var school = $('#school').val();
    
    // Make AJAX request to backend
    $.ajax({
        url: '/scrape',
        type: 'POST', // Change to POST method
        contentType: 'application/json',
        data: JSON.stringify({ school: school }), // Send selected school in request body
        success: function(data) {
            console.log('Scraping process initiated successfully.');
            // Call function to request logs
            fetchLogs();
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
}

function fetchLogs() {
    // Make AJAX request to fetch logs from Flask application
    $.ajax({
        url: '/receive-logs',
        type: 'GET',
        contentType: 'application/json',
        success: function(data) {
            // Display logs received from Flask application
            displayLogs(data);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching logs:', error);
        }
    });
}

function displayLogs(logs) {
    var logsHTML = '';

    // Iterate over each course in logs
    for (var course in logs) {
        // Display course name
        logsHTML += '<h2>' + course + '</h2>';

        // Iterate over events in sets of four
        for (var i = 0; i < logs[course].length; i += 4) {
            // Concatenate the first three events into one string
            var firstThreeEvents = logs[course].slice(i, i + 3).join(' ');

            // Get the fourth event
            var fourthEvent = logs[course][i + 3];

            // Display concatenated first three events
            logsHTML += '<p>' + firstThreeEvents + '</p>';

            // Display the fourth event separately
            logsHTML += '<p>' + fourthEvent + '</p>';
        }
    }

    // Display formatted logs on the page
    $('#logs').html(logsHTML);
}
