from flask import Flask, request, render_template, jsonify, send_from_directory
from yt_dlp import YoutubeDL, DownloadError
import logging
import os
import mimetypes

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # ⚠️ より安全な方法で設定する

logging.basicConfig(level=logging.INFO)

app.config['DOWNLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

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

    ydl_opts = {
        'format': format if choice == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s')
    }

    # TikTok動画の場合のフォーマット設定 (例)
    if 'tiktok.com' in url:
        ydl_opts['format'] = 'best'  # または確認した適切なフォーマットに変更

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            duration = info_dict.get('duration', 0)
            if duration > 360:
                return jsonify({'error': 'The video length exceeds 6 minutes and cannot be downloaded.'}), 400

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
        if "Unsupported URL" in str(e):
            return jsonify({'error': 'Unsupported URL. Please check the URL and try again.'}), 400
        elif "Requested format is not available" in str(e):
            return jsonify({'error': 'Requested format is not available for this video.'}), 400
        else:
            return jsonify({'error': f'Failed to generate download URL: {str(e)}'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

    # ファイルの種類によってMIMEタイプを設定
    ext = os.path.splitext(filename)[1]  # 拡張子を取得
    if ext in ['.mp3', '.wav']:
        mime_type = 'audio/mpeg' if ext == '.mp3' else 'audio/wav'
    elif ext == '.mp4':
        mime_type = 'video/mp4'
    else:
        # その他のファイル形式はデフォルトのMIMEタイプを使用
        mime_type = 'application/octet-stream'

    return send_from_directory(
        app.config['DOWNLOAD_FOLDER'],
        filename,
        as_attachment=True,
        mimetype=mime_type
    )

if __name__ == '__main__':
    app.run(debug=True)
