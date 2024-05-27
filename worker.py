from app import create_app

_, celery = create_app()  # create_app から celery を取得

if __name__ == '__main__':
    celery.worker_main()  # Celery ワーカーを開始
