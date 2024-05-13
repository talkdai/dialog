from dialog.settings import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase

engine = create_engine(Settings().DATABASE_URL)

class Base(DeclarativeBase):
    pass

def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session

