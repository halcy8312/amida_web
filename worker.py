from app import celery  # celery インスタンスのみをインポート

# タスクのインポート (必要であれば)
from app.tasks import download_video, download_audio

# ワーカーの実行
if __name__ == '__main__':
    celery.worker_main() 
