from typing import List

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select

from dialog.models import CompanyContent
from dialog.models.db import get_session
from dialog.settings import Settings
from dialog_lib.embeddings import generate


EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=Settings().OPENAI_API_KEY)

def generate_embeddings(documents: List[str]):
    return generate.generate_embeddings(documents, EMBEDDINGS_LLM)


def generate_embedding(document: str):
    """
    Generate embeddings for a single instance of document
    """
    return generate.generate_embedding(document, EMBEDDINGS_LLM)


def get_most_relevant_contents_from_message(message, top=5, dataset=None, session=None):
    return generate.get_most_relevant_contents_from_message(
        message, top, dataset, session, EMBEDDINGS_LLM, cosine_similarity_threshold=Settings().COSINE_SIMILARITY_THRESHOLD
    )