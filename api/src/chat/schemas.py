from datetime import datetime
from enum import Enum
from typing import List, Optional
from shared.db.models import Chat, ChatMessage
from sqlmodel import Field, SQLModel


class CreateChatPayload(SQLModel):
    name: str = Field()
    openai_model: Optional[str] = Field(default="gpt-4o-mini")
    initial_message_text: Optional[str] = Field(default=None)


class ReadChatResponse(SQLModel):
    id: int = Field()
    name: str = Field()
    openai_model: str = Field()
    openai_conversation_id: str = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
    messages: List[ChatMessage] = Field()

class CreateChatMessageRequest(SQLModel):
    message: str = Field()

class CreateChatMessagePayload(SQLModel):
    message: str = Field()
    chat_id: int = Field()
    openai_model: Optional[str] = Field(default="gpt-4o-mini")


class Route(str, Enum):
    DIRECT_LLM = "direct_llm"
    RAG = "rag"


class RouterResult(SQLModel):
    route: Route