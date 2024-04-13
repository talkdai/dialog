from typing import List

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select

from dialog.models import CompanyContent
from dialog.models.db import get_session
from dialog.settings import Settings
from dialog_lib.embeddings import generate


EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=Settings().OPENAI_API_KEY)