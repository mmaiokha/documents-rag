from sqlmodel import SQLModel, Field
import datetime
import sqlalchemy as sa
from enum import Enum


class UploadStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Upload(SQLModel, table=True):
    __tablename__ = "uploads"

    id: int | None = Field(default=None, primary_key=True, sa_type=sa.Integer)
    status: UploadStatus = Field(default=UploadStatus.PENDING, sa_type=sa.Enum(UploadStatus, name="upload_status"))
    file_name: str = Field(default=None, sa_type=sa.String)
    file_key: str = Field(sa_type=sa.String)
    file_bucket: str = Field(sa_type=sa.String)
    file_type: str = Field(default=None, sa_type=sa.String)
    file_size: int = Field(default=None, sa_type=sa.Integer)
    created_at: datetime.datetime = Field(default=None, sa_column_kwargs={"server_default": sa.text("CURRENT_TIMESTAMP")}, sa_type=sa.DateTime)
    updated_at: datetime.datetime = Field(default=None, sa_column_kwargs={"server_default": sa.text("CURRENT_TIMESTAMP")}, sa_type=sa.DateTime)