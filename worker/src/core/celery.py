from shared.celery import create_celery_client
from .settings import settings

celery_app = create_celery_client(settings.redis_url)