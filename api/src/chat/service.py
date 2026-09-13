from sqlalchemy import select
from typing import Annotated, List

from fastapi import Depends, HTTPException
from shared.db.models import Chat, ChatMessage, ChatMessageRole, Document, DocumentEmbeddings
from sqlmodel import Session
from chat.schemas import CreateChatMessagePayload, CreateChatPayload, Route, RouterResult
from core.settings import settings
from core.openai import OpenAIClient, OpenAIMessage
from fastapi.sse import ServerSentEvent

class ChatService:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def create_chat(self, payload: CreateChatPayload, session: Session):
        conversation = self.openai_client.create_conversation()

        chat = Chat(
            name=payload.name,
            openai_model=payload.openai_model,
            openai_conversation_id=conversation.id,
        )
        session.add(chat)
        session.commit()
        session.refresh(chat)

        yield ServerSentEvent(data=chat.model_dump(), event="chat_created")

        if payload.initial_message_text:
            yield from self.send_message(
                CreateChatMessagePayload(
                    message=payload.initial_message_text,
                    chat_id=chat.id,
                    openai_model=payload.openai_model,
                ),
                session,
            )

    def get_chat(self, chat_id: int, session: Session):
        chat = session.get(Chat, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        return chat

    def get_chats(self, session: Session):
        statement = select(Chat).order_by(Chat.created_at.desc())
        return session.exec(statement).all()

    def get_chat_messages(self, chat_id: int, session: Session):
        return session.exec(select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at.asc())).all()

    def route_message(self, payload: CreateChatMessagePayload, session: Session) -> RouterResult:
        prompt = """
            You are a routing model for a question-answering system.

            Your task is to determine whether the user's request requires
            searching a document database before generating an answer.

            Choose one of the following routes:
            DIRECT_LLM:
            - The question can be answered without searching the document database.
            - The user is asking for general knowledge, explanation, reasoning,
            writing, or another task that does not require information from
            the stored documents.

            RAG:
            - The user is asking about information that may be contained in
            the document database.
            - The user asks to find, search, retrieve, compare, summarize,
            or analyze information from the stored documents.
            - The answer may depend on specific facts, entities, or content
            contained in the documents.

            Important:
            - You do not know what kind of documents are stored in the database.
            - Do not assume that the documents are resumes, contracts, articles,
            or any other specific type of document.
            - If the user's request appears to require information from the
            stored documents, choose RAG.
            - Return only the structured routing result.
        """
        response = self.openai_client.parse_response(
            instructions=prompt,
            input=[OpenAIMessage(role=ChatMessageRole.USER, content=payload.message)],
            text_format=RouterResult,
        )
        return response

    def handle_message(self, payload: CreateChatMessagePayload, session: Session):
        router_result = self.route_message(payload, session)
        print(router_result)
        if router_result.route == Route.DIRECT_LLM:
            yield from self.send_message(payload, session)
        elif router_result.route == Route.RAG:
            yield from self.handle_rag_message(payload, session)

    def handle_rag_message(self, payload: CreateChatMessagePayload, session: Session):
        chat = self.get_chat(payload.chat_id, session)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        query_embedding = self.openai_client.create_embedding(payload.message)
        document_embeddings = session.exec(
            select(DocumentEmbeddings)
            .order_by(DocumentEmbeddings.embedding.cosine_distance(query_embedding))
            .limit(10)).scalars().all()

        print(document_embeddings)
        rag_context = self.generate_rag_context(document_embeddings)
        prompt = """
            You are a RAG model for a question-answering system.
            You will be given a question and a context of documents.
            You need to answer the question based on the context.
            If the question is not related to the context, say "I don't know".
            If the question is related to the context, answer the question based on the context.
        """

        context_prompt = f"The context is: {rag_context}"



        stream = self.openai_client.create_stream_message(
            conversation_id=chat.openai_conversation_id,
            model=chat.openai_model,
            messages=[
                OpenAIMessage(role="system", content=prompt), 
                OpenAIMessage(role="user", content=context_prompt),
                OpenAIMessage(role="user", content=payload.message),
            ],
        )

        user_message = ChatMessage(
            chat_id=payload.chat_id, role=ChatMessageRole.USER, message=payload.message
        )
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        llm_response_message = ChatMessage(
            chat_id=payload.chat_id, role=ChatMessageRole.ASSISTANT, message=""
        )

        for event in stream:
            if event.type == "response.created":
                yield ServerSentEvent(data=None, event="response_created")
            if event.type == "response.output_text.delta":
                yield ServerSentEvent(data={"text": event.delta}, event="response_updated")
            if event.type == "response.output_text.done":
                llm_response_message.message = event.text
                session.add(llm_response_message)
                session.commit()
                session.refresh(llm_response_message)
                yield ServerSentEvent(
                    data=llm_response_message.model_dump(), event="response_completed"
                )
        yield ServerSentEvent(raw_data="[DONE]", event="DONE")

    def generate_rag_context(self, embeddings: List[DocumentEmbeddings]):
        parts = []

        for embedding in embeddings:
    
            parts.append(f"""<document_embedding 
                document_id="{embedding.document_id}" 
                chunk_index="{embedding.chunk_index}">
                    {embedding.chunk_content}
                </document_embedding>""")

        return "\n".join(parts)
        
            
    def send_message(
        self, payload: CreateChatMessagePayload, session: Session
    ):

        chat = session.get(Chat, payload.chat_id)
        conversation = self.openai_client.get_conversation(chat.openai_conversation_id)

        user_message = ChatMessage(
            chat_id=payload.chat_id, role=ChatMessageRole.USER, message=payload.message
        )
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        llm_response_message = ChatMessage(
            chat_id=payload.chat_id, role=ChatMessageRole.ASSISTANT, message=""
        )

        response = self.openai_client.create_stream_message(
            conversation.id,
            payload.openai_model,
            [OpenAIMessage(role=user_message.role, content=user_message.message)],
        )

        for event in response:
            print(event)
            if event.type == "response.created":
                yield ServerSentEvent(data=None, event="response_created")
            if event.type == "response.output_text.delta":
                yield ServerSentEvent(data={"text": event.delta}, event="response_updated")
            if event.type == "response.output_text.done":

                llm_response_message.message = event.text
                session.add(llm_response_message)
                session.commit()
                session.refresh(llm_response_message)
                yield ServerSentEvent(
                    data=llm_response_message.model_dump(), event="response_completed"
                )

        yield ServerSentEvent(raw_data="[DONE]", event="DONE")


def get_chat_service():
    return ChatService(OpenAIClient(api_key=settings.openai_api_key))


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
