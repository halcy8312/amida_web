from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from yt_dlp import YoutubeDL, DownloadError
from pydub import AudioSegment
import os
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'

# ログ設定
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['choice']
    
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s')
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)
            logging.info(f"Downloaded file: {downloaded_file}")
            if choice == 'audio':
                format = request.form['format']
                audio = AudioSegment.from_file(downloaded_file)
                filename, ext = os.path.splitext(downloaded_file)
                new_file = f"{filename}.{format}"
                audio.export(new_file, format=format)
                os.remove(downloaded_file)
                downloaded_file = new_file
                logging.info(f"Converted file to {format}: {downloaded_file}")
    except DownloadError as e:
        flash(f'Failed to download: {str(e)}')
        logging.error(f"DownloadError: {str(e)}")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}')
        logging.error(f"Unexpected error: {str(e)}")
        return redirect(url_for('index'))
    
    filename = os.path.basename(downloaded_file)
    
    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
