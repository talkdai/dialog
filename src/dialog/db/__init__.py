from dialog.settings import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase

from contextlib import contextmanager

engine = create_engine(Settings().DATABASE_URL)


class Base(DeclarativeBase):
    pass

@contextmanager
def session_scope():
    with Session(bind=engine) as session:
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()

def get_session():
    with session_scope() as session:
        yield session