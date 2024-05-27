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
        current_app.logger.error(f'Error rendering template: {e}', exc_info=True)
        return "An error occurred", 500

@main.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    media_type = request.form['media_type']
    audio_format = request.form.get('audio_format', 'mp3')
    
    try:
        if media_type == 'video':
            result = download_video.delay(url)
        else:
            result = download_audio.delay(url, audio_format)
        
        result.wait()
        file_path = result.get()
        
        if not os.path.exists(file_path):
            current_app.logger.error(f'File not found: {file_path}')
            return "File not found", 404
        
        current_app.logger.debug(f'File downloaded successfully: {file_path}')
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f'Error during download: {e}', exc_info=True)
        return "An error occurred during download", 500
