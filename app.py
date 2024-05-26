from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from pytube import YouTube, exceptions as pytube_exceptions
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Flaskのセッション管理用の秘密鍵
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'

# YouTube URLの正規表現
YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['choice']
    format = request.form['format'] if choice == 'audio' else None
    
    try:
        if YOUTUBE_REGEX.match(url):
            # Use pytube for YouTube URLs
            yt = YouTube(url)
            if choice == 'video':
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            output_file = stream.download(output_path=app.config['DOWNLOAD_FOLDER'])
            if choice == 'audio' and format:
                audio = AudioSegment.from_file(output_file)
                filename, ext = os.path.splitext(output_file)
                new_file = f"{filename}.{format}"
                audio.export(new_file, format=format)
                os.remove(output_file)
                output_file = new_file
        else:
            # Use yt-dlp for other URLs
            ydl_opts = {
                'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s')
            }
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info_dict)
                if choice == 'audio' and format:
                    audio = AudioSegment.from_file(downloaded_file)
                    filename, ext = os.path.splitext(downloaded_file)
                    new_file = f"{filename}.{format}"
                    audio.export(new_file, format=format)
                    os.remove(downloaded_file)
                    downloaded_file = new_file
                output_file = downloaded_file
    except (pytube_exceptions.RegexMatchError, pytube_exceptions.VideoUnavailable):
        flash('Invalid YouTube URL or the video is unavailable. Please try another URL.')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Failed to download: {str(e)}')
        return redirect(url_for('index'))
    
    filename = os.path.basename(output_file)
    
    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
