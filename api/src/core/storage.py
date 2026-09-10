
from typing import Annotated

from core.settings import settings
from fastapi import Depends
from shared.storage import ObjectStorage


def get_object_storage() -> ObjectStorage:
    return ObjectStorage(
        settings.minio_url,
        access_key=settings.minio_user,
        secret_key=settings.minio_password,
        secure=settings.minio_secure
    )

ObjectStorageDep = Annotated[ObjectStorage, Depends(get_object_storage)]