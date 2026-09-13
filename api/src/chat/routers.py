
import asyncio
import random
from typing import AsyncIterable, List
from chat.schemas import CreateChatMessagePayload, CreateChatMessageRequest, CreateChatPayload, ReadChatResponse
from chat.service import ChatServiceDep
from core.database import SessionDep
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent


router = APIRouter(
    prefix="/chat",
    tags=["uploads"],
)

@router.post("/", response_class=EventSourceResponse)
def create_chat(
    body: CreateChatPayload,
    session: SessionDep,
    chat_service: ChatServiceDep
):
    yield from chat_service.create_chat(body, session)

@router.get("/")
async def get_chats(
    session: SessionDep,
    chat_service: ChatServiceDep
) -> List[ReadChatResponse]:
    return chat_service.get_chats(session)

@router.get("/{chat_id}")
async def get_chat(
    chat_id: int,
    session: SessionDep,
    chat_service: ChatServiceDep
) -> ReadChatResponse:
    return chat_service.get_chat(chat_id, session)

@router.post("/{chat_id}/messages", response_class=EventSourceResponse)
def create_message(
    chat_id: int,
    body: CreateChatMessageRequest,
    session: SessionDep,
    chat_service: ChatServiceDep
) -> AsyncIterable[ServerSentEvent]:
    yield from chat_service.handle_message(CreateChatMessagePayload(message=body.message, chat_id=chat_id), session)

# @router.get("/{chat_id}/messages/")
# async def get_messages(
#     chat_id: int,
#     session: SessionDep
# ) -> AsyncIterable[ServerSentEvent]:
#     pass