import copy
from datetime import timedelta
from typing import Annotated
from .models import Upload, UploadStatus
from core.storage import ObjectStorage, ObjectStorageDep
from .schemas import GenerateUpload, GenerateUploadResponse
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
import uuid


class UploadsService:
    def __init__(self, object_storage: ObjectStorage):
        self.object_storage = object_storage

    def generate_upload_url(
        self, data: GenerateUpload, session: Session
    ) -> GenerateUploadResponse:

        upload_id = uuid.uuid4()

        temporary_key = f"tmp/{upload_id}/{data.file_name}"

        presigned_url = self.object_storage.get_presigned_url(
            bucket=data.bucket, object_name=temporary_key
        )

        upload = Upload(
            file_name=data.file_name,
            file_key=temporary_key,
            file_bucket=data.bucket,
            file_type=data.file_type,
            file_size=data.file_size,
        )

        session.add(upload)
        session.commit()
        session.refresh(upload)

        return GenerateUploadResponse(
            **upload.model_dump(), presigned_url=presigned_url
        )

    def get_presigned_get_url(
        self,
        bucket: str,
        object_name: str,
        expires: timedelta = timedelta(minutes=15),
    ) -> str:
        return self.object_storage.get_presigned_get_url(
            bucket=bucket, object_name=object_name, expires=expires
        )

    def make_file_permanent(
        self,
        upload_id: int,
        session: Session,
    ) -> Upload:
        upload = session.get(Upload, upload_id)
        if not upload:
            raise HTTPException(status_code=404, detail="Uploaded filed does not exists")

        permanent_object_name = f"permanent/{upload.id}/{upload.file_name}"

        if not self.object_storage.file_exists(upload.file_bucket, upload.file_key):
            raise HTTPException(status_code=404, detail="Uploaded filed does not exists")

        self.object_storage.make_permanent(
            bucket=upload.file_bucket,
            source=upload.file_key,
            destination=permanent_object_name,
        )

        upload.file_key= permanent_object_name
        upload.status = UploadStatus.COMPLETED

        return upload


# Dependencies
def get_uploads_service(object_storage: ObjectStorageDep):
    return UploadsService(object_storage)


UploadsServiceDep = Annotated[UploadsService, Depends(get_uploads_service)]
