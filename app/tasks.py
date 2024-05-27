import youtube_dl
from celery import shared_task
import os
import logging

logger = logging.getLogger(__name__)

@shared_task
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
        logger.debug(f'Video downloaded successfully: {file_path}')
        return file_path
    except Exception as e:
        logger.error(f'Error downloading video: {e}', exc_info=True)
        raise

@shared_task
def download_audio(url, format):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
        logger.debug(f'Audio downloaded successfully: {file_path}')
        return file_path
    except Exception as e:
        logger.error(f'Error downloading audio: {e}', exc_info=True)
        raise
