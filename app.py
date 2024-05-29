from flask import Flask, request, render_template, jsonify, send_from_directory
from yt_dlp import YoutubeDL, DownloadError
import logging
import os
import urllib.parse

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

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    choice = data.get('choice')
    format = data.get('format')

    if not url:
        return jsonify({'error': 'URL is required.'}), 400

    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # クッキーファイルの設定（存在しない場合は設定しない）
    cookies_file = 'path/to/cookies.txt'
    if os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

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
            return jsonify({'download_url': f'/download_file/{urllib.parse.quote(file_name)}'}), 200
    except DownloadError as e:
        logging.error(f"DownloadError: {str(e)}")
        return jsonify({'error': f'Failed to generate download URL: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    # ファイル名をデコード
    filename = urllib.parse.unquote(filename)
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    
    # ファイルの存在確認
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found.'}), 404
    
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)