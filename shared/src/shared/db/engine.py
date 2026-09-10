
from sqlmodel import create_engine

def create_database_engine(database_url):
    return create_engine(database_url, echo=True)




