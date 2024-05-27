from flask import Flask
from celery import Celery
from flask_cors import CORS
import os

def create_app():

    celery = Celery(__name__, broker=os.getenv('CELERY_BROKER_URL'))

    app = Flask(__name__, template_folder='../templates')
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    CORS(app)

    from .routes import main
    app.register_blueprint(main)

    # Celery 設定を Flask アプリケーションのコンテキスト内で行う
    def make_celery(app):
        celery.conf.update(app.config)
        TaskBase = celery.Task
        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        celery.Task = ContextTask
        return celery

    celery = make_celery(app)

    # タスクの自動登録を関数内で行う
    import app.tasks 

    return app, celery
