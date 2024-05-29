from flask import Flask, request, render_template, jsonify, send_file
from yt_dlp import YoutubeDL, DownloadError
import logging
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ログ設定
logging.basicConfig(level=logging.INFO)

# ダウンロードフォルダの設定
app.config['DOWNLOAD_FOLDER'] = 'downloads'

# ダウンロードフォルダが存在しない場合は作成
if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
    os.makedirs(app.config['DOWNLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()  # JSON形式のリクエストデータを取得
    url = data.get('url')
    choice = data.get('choice')
    format = data.get('format')
    
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s')
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            duration = info_dict.get('duration', 0)
            if duration > 360:
                return jsonify({'error': 'The video length exceeds 6 minutes and cannot be downloaded.'}), 400
            
            # ファイルパスを取得
            file_path = ydl.prepare_filename(info_dict)
            if choice == 'audio':
                audio_file = f"{os.path.splitext(file_path)[0]}.{format}"
                os.rename(file_path, audio_file)
                file_path = audio_file
            
            file_name = os.path.basename(file_path)
            
            logging.info(f"Generated file path: {file_path}")
            return jsonify({'download_url': f'/download_file/{file_name}'}), 200
    except DownloadError as e:
        logging.error(f"DownloadError: {str(e)}")
        return jsonify({'error': f'Failed to generate download URL: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return jsonify({'error': 'File not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)