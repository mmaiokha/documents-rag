
from .models import Document
from sqlmodel import SQLModel, Field
import sqlalchemy as sa



class CreateDocument(SQLModel):
    name: str = Field(sa_type=sa.String)
    description: str = Field(sa_type=sa.String)
    uploads_id: int = Field(sa_type=sa.Integer)

class ReadDocument(Document):
    file_url: str = Field(sa_type=sa.String)