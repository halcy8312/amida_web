document.getElementById('download-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var urlInput = document.getElementById('url');
    var choiceSelect = document.getElementById('choice');
    var selectedFormat = document.getElementById('selected-format').value; // 追加: 選択された音声形式

    // フォーム送信時に以前のメッセージとリンクをクリア
    document.getElementById('message').style.display = 'none';
    document.getElementById('download-link').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: urlInput.value,
            choice: choiceSelect.value,
            format: selectedFormat // 追加: 選択された音声形式
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.error) {
            document.getElementById('message').style.display = 'block';
            document.getElementById('message').innerText = data.error;
        } else {
            const downloadUrl = data.download_url;
            const downloadLink = document.getElementById('download-url');
            const filename = downloadUrl.split('/').pop(); // ファイル名を取得
            downloadLink.href = downloadUrl;
            downloadLink.download = filename; // ダウンロード属性を設定
            document.getElementById('download-link').style.display = 'block';
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
