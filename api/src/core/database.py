from typing import Annotated
from .settings import settings
from sqlmodel import create_engine, Session, SQLModel
from fastapi import Depends


DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]