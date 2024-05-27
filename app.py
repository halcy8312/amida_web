from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, jsonify
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
from celery import Celery, current_task

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'insecure_key_for_dev_only')
app.config['DOWNLOAD_FOLDER'] = 'downloads/'

# Celery設定
celery_broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_result_backend = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')

celery = Celery(app.name, broker=celery_broker_url, backend=celery_result_backend)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        current_task.update_state(state='PROGRESS', meta={'percent': percent})

@celery.task(bind=True)
def download_and_convert(self, url, choice, format, download_folder):
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title).40s.%(ext)s'),  # タイトルを最大40文字に制限
        'noplaylist': True,
        'progress_hooks': [progress_hook],
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

        return {'status': 'COMPLETED', 'result': os.path.basename(downloaded_file)}
    except Exception as e:
        app.logger.error(f"Download failed: {e}")
        return {'status': 'FAILED', 'result': f"Error: {str(e)}"}

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
    
    task = download_and_convert.apply_async(args=[url, choice, format, app.config['DOWNLOAD_FOLDER']])
    return jsonify({'task_id': task.id})

@app.route('/status/<task_id>')
def check_status(task_id):
    task = download_and_convert.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': 'Downloading...',
            'progress': task.info.get('percent', 0)
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info['status'] if isinstance(task.info, dict) else str(task.info)
        }
        if isinstance(task.info, dict) and 'result' in task.info:
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
    if task.state == 'SUCCESS' and isinstance(task.info, dict):
        filename = task.info['result']
        return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)
    else:
        flash('File is not ready yet, please check back later.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
