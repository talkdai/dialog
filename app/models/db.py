from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

try:
    from app.settings import DATABASE_URL
except:
    from settings import DATABASE_URL


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))