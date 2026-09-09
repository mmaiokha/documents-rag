from typing import Annotated
from .models import Upload
from core.storage import ObjectStorage, ObjectStorageDep
from .schemas import GenerateUpload
from sqlmodel import Session
from fastapi import Depends
import uuid 


class UploadsService:
    def __init__(self, object_storage: ObjectStorage):
        self.object_storage = object_storage

    def generate_upload_url(
        self, data: GenerateUpload, session: Session
    ) -> Upload:

        upload_id = uuid.uuid4()

        object_name = f"tmp/{upload_id}/{data.file_name}"

        presigned_url = self.object_storage.get_presigned_url(
            bucket=data.bucket, object_name=object_name
        )

        upload = Upload(
            file_name=data.file_name,
            file_path=presigned_url,
            file_type=data.file_type,
            file_size=data.file_size,
        )

        session.add(upload)
        session.commit()
        session.refresh(upload)
        
        return upload


# Dependencies
def get_uploads_service(object_storage: ObjectStorageDep):
    return UploadsService(object_storage)


UploadsServiceDep = Annotated[UploadsService, Depends(get_uploads_service)]
