from flask import Flask, request, render_template, jsonify
from yt_dlp import YoutubeDL, DownloadError
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ログ設定
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # JSON形式のリクエストデータを取得
    url = data.get('url')
    choice = data.get('choice')
    
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'noplaylist': True,
        'quiet': True
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            duration = info_dict.get('duration', 0)
            if duration > 360:
                return jsonify({'error': 'The video length exceeds 6 minutes and cannot be downloaded.'}), 400
            
            # ダウンロードURLを取得
            formats = info_dict.get('formats', [])
            if choice == 'audio':
                download_url = next((f['url'] for f in formats if f['ext'] == 'm4a'), None)
            else:
                download_url = next((f['url'] for f in formats if f['ext'] == 'mp4'), None)
            
            if not download_url:
                return jsonify({'error': 'Failed to find a suitable download URL.'}), 500
            
            logging.info(f"Generated download URL: {download_url}")
            return jsonify({'download_url': download_url}), 200
    except DownloadError as e:
        logging.error(f"DownloadError: {str(e)}")
        return jsonify({'error': f'Failed to generate download URL: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}')}), 500

if __name__ == '__main__':
    app.run(debug=True)
