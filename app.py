from flask import Flask, request, render_template, jsonify, send_from_directory
import logging
import os
import urllib.parse
from pytube import YouTube

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

    try:
        yt = YouTube(url)
        if choice == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

        if not stream:
            return jsonify({'error': 'No suitable stream found.'}), 400

        duration = yt.length
        if duration > 360:
            return jsonify({'error': 'The video length exceeds 6 minutes and cannot be downloaded.'}), 400

        file_path = stream.download(output_path=app.config['DOWNLOAD_FOLDER'])
        if choice == 'audio' and format:
            base, _ = os.path.splitext(file_path)
            new_file_path = base + '.' + format
            os.rename(file_path, new_file_path)
            file_path = new_file_path

        file_name = os.path.basename(file_path)
        logging.info(f"Generated file path: {file_path}")
        return jsonify({'download_url': f'/download_file/{urllib.parse.quote(file_name)}'}), 200
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    filename = urllib.parse.unquote(filename)
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found.'}), 404

    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)