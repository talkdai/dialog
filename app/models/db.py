from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

try:
    from app.settings import DB_URL
except:
    from settings import DB_URL


engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()
session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))