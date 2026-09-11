from openai import OpenAI

from core.settings import settings

openai = OpenAI(
    api_key=settings.openai_api_key
)