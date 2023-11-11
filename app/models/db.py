from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from decouple import config

url = URL.create(
    drivername="postgresql",
    username=config("PSQL_USER"),
    password=config("PSQL_PASSWORD"),
    host=config("PSQL_HOST", default="localhost"),
    database=config("PSQL_DATABASE", default="talkdai"),
    port=config("PSQL_PORT", default="5432"),
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()
session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))