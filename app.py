　<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloader</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>Download YouTube Video or Audio</h1>
    <form id="download-form" method="POST">
        <label for="url">YouTube URL:</label>
        <input type="text" id="url" name="url" required>
        <br>
        <label for="downloadType">Download Type:</label>
        <select id="downloadType" name="downloadType" required>
            <option value="video">Video</option>
            <option value="audio">Audio</option>
        </select>
        <br>
        <label for="format">Format (for audio only):</label>
        <select id="format" name="format">
            <option value="mp3">MP3</option>
            <option value="wav">WAV</option>
        </select>
        <br>
        <button type="submit">Download</button>
    </form>
    <div id="status"></div>
    <div id="download-link"></div>
    
    <script>
        $(document).ready(function() {
            $('#download-form').submit(function(event) {
                event.preventDefault();
                $('#status').text('Starting download...');
                $('#download-link').html('');

                $.post('/download', $(this).serialize(), function(data) {
                    checkStatus(data.task_id);
                });
            });

            function checkStatus(task_id) {
                $.get('/status/' + task_id, function(data) {
                    if (data.state === 'PENDING' || data.state === 'PROGRESS') {
                        $('#status').text(data.status + ' ' + (data.progress || ''));
                        setTimeout(function() {
                            checkStatus(task_id);
                        }, 1000);
                    } else if (data.state === 'SUCCESS') {
                        $('#status').text('Download complete!');
                        $('#download-link').html('<a href="/download/file/' + task_id + '">Click here to download</a>');
                    } else {
                        $('#status').text('Error: ' + data.status);
                    }
                });
            }
        });
    </script>
</body>
</html>
