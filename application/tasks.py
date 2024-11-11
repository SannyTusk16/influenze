from celery import Celery
from app import app_celery

@app_celery.task()
def func():
    print(46)