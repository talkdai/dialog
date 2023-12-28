from typing import List

from langchain.embeddings import OpenAIEmbeddings
from sqlalchemy import select

from dialog.models import CompanyContent
from dialog.models.db import session
from dialog.settings import OPENAI_API_KEY


EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def generate_embeddings(documents: List[str]):
    """
    Generate embeddings for a list of documents
    """
    return EMBEDDINGS_LLM.embed_documents(documents)


def generate_embedding(document: str):
    """
    Generate embeddings for a single instance of document
    """
    return EMBEDDINGS_LLM.embed_query(document)


def get_most_relevant_contents_from_message(message, top=5, dataset=None):
    message_embedding = generate_embedding(message)
    filters = [
        CompanyContent.embedding.l2_distance(message_embedding) < 1,
    ]

    if dataset is not None:
        filters.append(CompanyContent.dataset == dataset)

    possible_contents = session.scalars(
        select(CompanyContent)
        .filter(*filters)
        .order_by(CompanyContent.embedding.l2_distance(message_embedding).asc())
        .limit(top)
    ).all()
    return possible_contents