from sqlmodel import SQLModel, Field
import datetime
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True, sa_type=sa.Integer)
    name: str = Field(default=None, sa_type=sa.String)
    description: str = Field(default=None, sa_type=sa.String)
    file_key: str  = Field(sa_type=sa.String)
    file_bucket: str | None = Field(default=None, sa_type=sa.String)
    file_type: str = Field(sa_type=sa.String)
    file_size: int = Field(sa_type=sa.Integer)

    created_at: datetime.datetime = Field(default=None, sa_column_kwargs={"server_default": sa.text("CURRENT_TIMESTAMP")}, sa_type=sa.DateTime)
    updated_at: datetime.datetime = Field(default=None, sa_column_kwargs={"server_default": sa.text("CURRENT_TIMESTAMP")}, sa_type=sa.DateTime)


class DocumentEmbeddings(SQLModel, table = True):
    __tablename__ = "documents_embeddings"

    id: int | None = Field(default=None, primary_key=True, sa_type=sa.Integer)
    document_id: int = Field(index=True, foreign_key="documents.id")

    chunk_index: int= Field(sa_type=sa.Integer)

    chunk_content: str= Field(sa_type=sa.String)

    page_start: int= Field(sa_type=sa.Integer)
    page_end: int = Field(sa_type=sa.Integer)

    embedding: list[float] = Field(
        sa_column=sa.Column(Vector(1536))
    )