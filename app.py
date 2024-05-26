from flask import Flask, request, render_template, send_from_directory
from pytube import YouTube
import os

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['choice']
    yt = YouTube(url)
    
    if choice == 'video':
        stream = yt.streams.get_highest_resolution()
    else:
        stream = yt.streams.filter(only_audio=True).first()
    
    output_file = stream.download(output_path=app.config['DOWNLOAD_FOLDER'])
    filename = os.path.basename(output_file)
    
    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
