from datetime import timedelta
from typing import Annotated
from minio import Minio
from core.settings import settings
from fastapi import Depends



class ObjectStorage:
    def __init__(self, endpoint, access_key, secret_key, secure = True):
    
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )


    def get_presigned_url(
        self, bucket, object_name, expires: timedelta = timedelta(minutes=15)
    ) -> str:
        return self.client.presigned_put_object(bucket, object_name, expires)


def get_object_storage() -> ObjectStorage:
    print(settings.minio_secure)
    return ObjectStorage(
        settings.minio_url,
        access_key=settings.minio_user,
        secret_key=settings.minio_password,
        secure=settings.minio_secure
    )

ObjectStorageDep = Annotated[ObjectStorage, Depends(get_object_storage)]