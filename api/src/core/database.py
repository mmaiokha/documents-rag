from typing import Annotated
from .settings import settings
from sqlmodel import Session
from fastapi import Depends

from shared.db import create_database_engine


engine = create_database_engine(settings.database_url)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]