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
    url = request.form['url']
    choice = request.form['choice']
    
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            duration = info_dict.get('duration', 0)
            if duration > 360:
                return jsonify({'error': 'The video length exceeds 6 minutes and cannot be downloaded.'}), 400
            
            download_url = ydl.prepare_filename(info_dict)
            logging.info(f"Generated download URL: {download_url}")
            
            return jsonify({'download_url': download_url}), 200
    except DownloadError as e:
        logging.error(f"DownloadError: {str(e)}")
        return jsonify({'error': f'Failed to generate download URL: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
