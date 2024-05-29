from flask import Flask, render_template, request, send_file
import os
from pytube import YouTube
import subprocess
import requests
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            return "Access Denied: 403 Forbidden"
        
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').first()
        out_file = video.download(output_path='downloads')
        
        if format == 'mp3':
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            subprocess.run(['ffmpeg', '-i', out_file, new_file])
        elif format == 'wav':
            base, ext = os.path.splitext(out_file)
            new_file = base + '.wav'
            subprocess.run(['ffmpeg', '-i', out_file, new_file])
        else:
            new_file = out_file
        
        time.sleep(5)  # リクエストの間隔を空ける
        return send_file(new_file, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)