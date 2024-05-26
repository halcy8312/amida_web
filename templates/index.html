from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from pytube import YouTube, exceptions
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Flaskのセッション管理用の秘密鍵
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['choice']
    
    try:
        yt = YouTube(url)
    except exceptions.RegexMatchError:
        flash('Invalid YouTube URL. Please try again.')
        return redirect(url_for('index'))
    except exceptions.VideoUnavailable:
        flash('The video is unavailable. Please try another URL.')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))
    
    if choice == 'video':
        stream = yt.streams.get_highest_resolution()
    else:
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    
    try:
        output_file = stream.download(output_path=app.config['DOWNLOAD_FOLDER'])
    except Exception as e:
        flash(f'Failed to download: {str(e)}')
        return redirect(url_for('index'))
    
    filename = os.path.basename(output_file)
    
    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
