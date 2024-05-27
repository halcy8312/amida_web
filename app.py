from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'insecure_key_for_dev_only')  # 安全なキーを設定
app.config['DOWNLOAD_FOLDER'] = 'downloads/'

def download_and_convert(url, choice, format, download_folder):
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'audio' else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,  # 再生リストのダウンロードを防ぐ
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

            if choice == 'audio':
                audio = AudioSegment.from_file(downloaded_file)
                filename, _ = os.path.splitext(downloaded_file)  # 拡張子を使用しないため _ で受ける
                new_file = f"{filename}.{format}"
                audio.export(new_file, format=format)
                os.remove(downloaded_file)
                downloaded_file = new_file

        return os.path.basename(downloaded_file)  # ファイル名のみを返す
    except Exception as e:
        # エラー処理を強化
        app.logger.error(f"Download failed: {e}")  # エラーログを記録
        return f"Error: {str(e)}"  # エラーメッセージを返す

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return download()  # POSTリクエストの場合はダウンロード処理を実行
    return render_template('index.html')  # GETリクエストの場合はindex.htmlを返す

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    choice = request.form['downloadType']
    format = request.form.get('format', 'mp3')
    
    filename = download_and_convert(url, choice, format, app.config['DOWNLOAD_FOLDER'])
    if filename.startswith("Error:"):
        flash('Failed to download: ' + filename)
        return redirect(url_for('index'))
    return redirect(url_for('send_file', filename=filename))

@app.route('/download/<filename>')
def send_file(filename):
    response = send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=filename, as_attachment=True)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"  # Content-Dispositionヘッダーを追加
    return response

if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(debug=True)
