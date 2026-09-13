from dataclasses import dataclass
from typing import List, Type
from openai import OpenAI
from sqlmodel import SQLModel

from core.settings import settings

@dataclass
class OpenAIMessage:
    role: str
    content: str

DEFAULT_MODEL = "gpt-5.6"

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def create_conversation(self):
        return self.client.conversations.create()

    def get_conversation(self, conversation_id: str):
        return self.client.conversations.retrieve(
            conversation_id=conversation_id
        )

    def create_stream_message(self, conversation_id: str, model: str, messages: List[OpenAIMessage]):
        input_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        return self.client.responses.create(
            model=model,
            input=input_messages,
            stream=True,
            conversation=conversation_id
        )

    def parse_response(self, instructions: str, input: List[OpenAIMessage], text_format: Type[SQLModel], model: str = DEFAULT_MODEL):
        input_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in input
        ]
        response = self.client.responses.parse(
            model="gpt-5.6",
            instructions=instructions,
            input=input_messages,
            text_format=text_format,
        )

        return response.output_parsed

    def create_embedding(self, text: str):
        response = self.client.embeddings.create(
            model=settings.embeddings_model,
            input=text,
        )
        return response.data[0].embedding
