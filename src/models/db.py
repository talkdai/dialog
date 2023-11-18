from settings import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()
