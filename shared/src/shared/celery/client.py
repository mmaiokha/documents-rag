from celery import Celery

def create_celery_client(broker_url: str):
    return Celery('documents', broker=broker_url)