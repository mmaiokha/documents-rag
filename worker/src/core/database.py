from .settings import settings
from sqlmodel import Session

from shared.db import create_database_engine


engine = create_database_engine(settings.database_url)

def get_session():
    return Session(engine)
