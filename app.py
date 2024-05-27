import os
from flask import Flask, render_template, request, jsonify
from celery import Celery

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
app.config['CELERY_RESULT_BACKEND'] = os.environ['CELERY_RESULT_BACKEND']

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from tasks import download_video

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        media_type = request.form['media_type']
        audio_format = request.form.get('audio_format')
        task = download_video.delay(url, media_type, audio_format)
        return jsonify({'task_id': task.id})
    return render_template('index.html')

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = download_video.AsyncResult(task_id)
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
