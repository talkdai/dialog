from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dialog.settings import DATABASE_URL

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    engine = create_engine(DATABASE_URL)

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

Base = declarative_base()
