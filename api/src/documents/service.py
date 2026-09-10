from typing import Annotated

from shared.db.models import Document
from .schemas import CreateDocument, ReadDocument
from uploads.service import UploadsService, UploadsServiceDep
from fastapi import Depends
from sqlmodel import Session


class DocumentsService:
    def __init__(self, uploads_service: UploadsService):
        self.uploads_service = uploads_service

    def create(self, data: CreateDocument, session: Session) -> ReadDocument:

        upload = self.uploads_service.make_file_permanent(
            data.uploads_id, session=session
        )

        document = Document(
            name=data.name,
            description=data.description,
            file_bucket=upload.file_bucket,
            file_key=upload.file_key,
            file_type=upload.file_type,
            file_size=upload.file_size,
        )

        session.add(document)
        session.commit()
        session.refresh(document)

        file_url = self.uploads_service.get_presigned_get_url(upload.file_bucket, object_name=upload.file_key)


        return ReadDocument(
            **document.model_dump(),
            file_url=file_url,
        )


def get_documents_service(uploads_service: UploadsServiceDep):
    return DocumentsService(uploads_service=uploads_service)


DocumentsServiceDep = Annotated[DocumentsService, Depends(get_documents_service)]
