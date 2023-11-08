"""
this is for access celery worker and using it as client for sending tasks
"""

import os
from celery import Celery

celery_client = Celery(
    "tasks",
    broker=os.environ.get('CELERY_BROKER_URL'),
    backend=os.environ.get('CELERY_RESULT_BACKEND'),
)
