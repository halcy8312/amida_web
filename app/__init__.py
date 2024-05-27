from flask import Flask
from celery import Celery
from flask_cors import CORS
import os
import logging

celery = Celery(__name__, broker=os.getenv('CELERY_BROKER_URL'))

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    CORS(app)

    logging.basicConfig(level=logging.DEBUG)
    app.logger.debug(f"CELERY_BROKER_URL: {os.getenv('CELERY_BROKER_URL')}")
    app.logger.debug(f"CELERY_RESULT_BACKEND: {os.getenv('CELERY_RESULT_BACKEND')}")
    app.logger.debug(f"FLASK_SECRET_KEY: {os.getenv('FLASK_SECRET_KEY')}")

    from .routes import main
    app.register_blueprint(main)

    celery.conf.update(app.config)

    with app.app_context():
        import app.tasks

    return app
