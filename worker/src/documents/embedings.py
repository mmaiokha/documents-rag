from core.database import get_session
from core.openai import openai
from core.settings import settings
from documents.process_pdf import Chunk
from shared.db.models import DocumentEmbeddings

def embed_chunk(chunk: Chunk, document_id: int) -> None:
    response = openai.embeddings.create(
        model=settings.embeddings_model,
        input=chunk.content
    )

    embedding = response.data[0].embedding
    
    session = get_session()

    document_embedding = DocumentEmbeddings(
        chunk_content=chunk.content,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        document_id=document_id,
        chunk_index=chunk.chunk_index,
        embedding=embedding
    )

    session.add(document_embedding)
    session.commit()