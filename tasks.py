from celery import Celery
from app import celery  
import yt_dlp as youtube_dl


@celery.task(bind=True)
def download_video(self, url, media_type, audio_format=None):
    try:
        ydl_opts = {
            'format': 'bestaudio/best' if media_type == 'audio' else 'bestvideo+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [self.update_state],
        }
        if media_type == 'audio' and audio_format:
            ydl_opts['format'] = audio_format

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info_dict)
            return {'status': 'Download complete', 'result': filename}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'status': f'Download failed: {e}'})
        raise 
