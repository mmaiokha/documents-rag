from core.database import SessionDep
from .service import DocumentsServiceDep
from .schemas import CreateDocument
from fastapi import APIRouter

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.get("/")
async def get_documents():
    return {"message": "Documents fetched successfully"}


@router.post("/")
async def create_document(data: CreateDocument, session: SessionDep, service: DocumentsServiceDep):
    return service.create(data, session)