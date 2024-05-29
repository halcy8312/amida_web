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

# ... (その他のルート: /privacy, /terms, /contact)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    choice = data.get('choice')
    format = data.get('format')  # 追加: 音声形式

    ydl_opts = {
        'format': format if choice == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # format を動的に設定
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
    # ファイルの拡張子からMIMEタイプを推測 (より正確な方法は別途調べる)
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True, mimetype=mime_type)

if __name__ == '__main__':
    app.run(debug=True)
