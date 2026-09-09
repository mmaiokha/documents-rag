from .service import UploadsServiceDep
from core.database import SessionDep
from fastapi import APIRouter
from uploads.schemas import GenerateUpload, ReadUpload
from sqlmodel import Session

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
)


@router.post("/presigned-url", response_model=ReadUpload)
async def get_presigned_url(
    body: GenerateUpload,
    service: UploadsServiceDep,
    session: SessionDep
):
    return service.generate_upload_url(body, session=session)
