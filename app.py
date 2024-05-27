from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, jsonify
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
from celery import Celery

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'insecure_key_for_dev_only')
app.config['DOWNLOAD_FOLDER'] = 'downloads/'

# Celery設定
celery_broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_result_backend = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')

celery = Celery(app.name, broker=celery_broker_url, backend=celery_result_backend)

@celery.task
def download_and_convert(url, choice, format, download_folder):
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

            if choice == 'audio':
                audio = AudioSegment.from_file(downloaded_file)
                filename, _ = os.path.splitext(downloaded_file)
                new_file = f"{filename}.{format}"
                audio.export(new_file, format=format)
                os.remove(downloaded_file)
                downloaded_file = new_file

        return os.path.basename(downloaded_file)
    except Exception as e:
        app.logger.error(f"Download failed: {e}")
        return f"Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return download()
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['downloadType']
    format = request.form.get('format', 'mp3')
    
    task = download_and_convert.delay(url, choice, format, app.config['DOWNLOAD_FOLDER'])
    return redirect(url_for('check_status', task_id=task.id))

@app.route('/status/<task_id>')
def check_status(task_id):
    task = download_and_convert.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.route('/download/file/<task_id>')
def download_file(task_id):
    task = download_and_convert.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        filename = task.result
        return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)
    else:
        flash('File is not ready yet, please check back later.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
