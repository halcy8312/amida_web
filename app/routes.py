from flask import Blueprint, render_template, request, send_file
from .tasks import download_video, download_audio
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    media_type = request.form['media_type']
    audio_format = request.form.get('audio_format', 'mp3')
    
    if media_type == 'video':
        result = download_video.delay(url)
    else:
        result = download_audio.delay(url, audio_format)
    
    result.wait()
    file_path = result.get()
    
    return send_file(file_path, as_attachment=True)
