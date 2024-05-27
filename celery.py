from __future__ import absolute_import, unicode_literals
from app import make_celery, app

celery = make_celery(app)
