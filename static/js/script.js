// 他の既存のコードがある場合はそのままにして、新しいコードを追加します。

document.getElementById('download-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var url = document.getElementById('url').value;
    var choice = document.getElementById('choice').value;
    var format = document.getElementById('selected-format').value;
    var cookies = document.cookie;  // クッキー情報を取得

    // フォーム送信時に以前のメッセージとリンクをクリア
    document.getElementById('message').style.display = 'none';
    document.getElementById('download-link').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    
    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url, choice: choice, format: format, cookies: cookies }),  // クッキー情報を送信
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.error) {
            document.getElementById('message').style.display = 'block';
            document.getElementById('message').innerText = data.error;
        } else {
            const downloadUrl = data.download_url;
            const downloadLink = document.getElementById('download-url');
            downloadLink.href = downloadUrl;
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