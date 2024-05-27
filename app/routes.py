from flask import Blueprint, render_template, request, send_file, current_app
from .tasks import download_video, download_audio
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    try:
        current_app.logger.debug('Rendering index.html')
        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f'Error rendering template: {e}')
        return "An error occurred", 500

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
