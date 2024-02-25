from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings

from dialog.settings import COLLECTION_NAME, DATABASE_URL

class CustomPGVector(PGVector):
    """
    Custom wrapper for Langchain's PGVector class that allows custom functionalities.
    """
    def __init__(self):
        super().__init__(collection_name=COLLECTION_NAME, connection_string=DATABASE_URL, embedding_function=OpenAIEmbeddings())
