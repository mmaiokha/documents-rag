from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy as sa

class Chat(SQLModel, table=True):
    __tablename__= "chats"

    id: Optional[int] = Field(default=None, primary_key=True, sa_type=sa.Integer)
    openai_model: str = Field(index=True, default="gpt-4o-mini", sa_type=sa.String(255))
    openai_conversation_id: str = Field(index=True, sa_type=sa.String(255))
    name: str = Field(index=True, sa_type=sa.String(255))
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now(), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})

    messages: List[ChatMessage] = Relationship(back_populates="chat")
    

class ChatMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(SQLModel, table=True):
    __tablename__= "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True, sa_type=sa.Integer)
    chat_id: int = Field(foreign_key="chats.id", index=True, sa_type=sa.Integer)
    message: str = Field(index=True, sa_type=sa.Text)
    role: ChatMessageRole = Field(index=True, default=ChatMessageRole.USER, sa_type=sa.Enum(ChatMessageRole))
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now(), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})

    chat: Chat = Relationship(back_populates="messages")
