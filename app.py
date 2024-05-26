from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
from celery import Celery

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'

# 環境変数からCeleryの設定を読み込む
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['RESULT_BACKEND'] = os.getenv('RESULT_BACKEND')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# 非推奨設定の対応
celery.conf.update({
    'broker_connection_retry_on_startup': True
})

@celery.task
def download_and_convert(url, choice, format, download_folder):
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s')
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)
            if choice == 'audio':
                audio = AudioSegment.from_file(downloaded_file)
                filename, ext = os.path.splitext(downloaded_file)
                new_file = f"{filename}.{format}"
                audio.export(new_file, format=format)
                os.remove(downloaded_file)
                downloaded_file = new_file
        return os.path.basename(downloaded_file)
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['choice']
    format = request.form.get('format', 'mp3')
    
    task = download_and_convert.delay(url, choice, format, app.config['DOWNLOAD_FOLDER'])
    flash('Download started. Please check back later.')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def send_file(filename):
    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
