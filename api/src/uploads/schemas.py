from shared.db.models.uploads import Upload
from sqlmodel import SQLModel, Field
import sqlalchemy as sa


class GenerateUpload(SQLModel):
    file_name: str = Field(sa_type=sa.String)
    file_type: str = Field(sa_type=sa.String)
    file_size: int = Field(sa_type=sa.Integer)
    bucket: str = Field(sa_type=sa.String)

class GenerateUploadResponse(Upload):
    presigned_url: str = Field(sa_type=sa.String)

class ReadUpload(Upload):
    pass