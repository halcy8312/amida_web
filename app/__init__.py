from flask import Flask
from celery import Celery
from flask_cors import CORS

celery = Celery(__name__, broker='redis://localhost:6379/0')

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../.env')
    CORS(app)

    from .routes import main
    app.register_blueprint(main)

    celery.conf.update(app.config)

    return app
