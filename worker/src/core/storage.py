
from io import BytesIO

from core.settings import settings
from shared.storage import ObjectStorage



object_storage = ObjectStorage(
        settings.minio_url,
        access_key=settings.minio_user,
        secret_key=settings.minio_password,
        secure=settings.minio_secure
    )

client = object_storage.client

def read_from_minio(bucket: str, object_key: str) -> BytesIO:
    response = client.get_object(bucket, object_key)

    try:
        return BytesIO(response.read())
    finally:
        response.close()
        response.release_conn()