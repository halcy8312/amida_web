from app import create_app, celery
from app.tasks import download_video, download_audio  # タスクのインポート

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        celery.start()
