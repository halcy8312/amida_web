document.getElementById('download-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var url = document.getElementById('url').value;
    var choice = document.getElementById('choice').value;
    var format = document.getElementById('selected-format').value;

    // フォーム送信時に以前のメッセージとリンクをクリア
    document.getElementById('message').style.display = 'none';
    document.getElementById('download-link').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    
    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url, choice: choice, format: format }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.error) {
            document.getElementById('message').style.display = 'block';
            document.getElementById('message').innerText = data.error;
        } else {
            document.getElementById('download-link').style.display = 'block';
            document.getElementById('download-url').href = data.download_url;
        }
    })
    .catch((error) => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('message').style.display = 'block';
        document.getElementById('message').innerText = 'An unexpected error occurred.';
        console.error('Error:', error);
    });
});

function selectFormat(format) {
    document.getElementById('selected-format').value = format;
    document.getElementById('mp3-button').classList.remove('selected');
    document.getElementById('wav-button').classList.remove('selected');
    document.getElementById(format + '-button').classList.add('selected');
}

window.onload = function() {
    selectFormat('mp3');
    document.getElementById('choice').value = 'audio';
    document.getElementById('audio-format').style.display = 'flex';
}

document.getElementById('choice').addEventListener('change', function () {
    var choice = this.value;
    if (choice === 'audio') {
        document.getElementById('audio-format').style.display = 'flex';
    } else {
        document.getElementById('audio-format').style.display = 'none';
    }
});
