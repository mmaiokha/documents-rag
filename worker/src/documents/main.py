from core.celery import celery_app
from shared.db.models import Document
from shared.tasks.documents import PROCESS_DOCUMENT
from core.database import get_session
from documents.embedings import embed_chunk
from .process_pdf import parse_pdf, chunk_pages

@celery_app.task(name=PROCESS_DOCUMENT)
def process_document(document_id: str):
    print(f"Processing document {document_id}")

    with get_session() as session:
            

        document = session.get(Document, document_id)

        parsed_document = parse_pdf(document.file_bucket, document.file_key)

        chunks = chunk_pages(parsed_document)

        for chunk in chunks:
            embed_chunk(chunk=chunk, document_id=document_id)

        print(chunks)

