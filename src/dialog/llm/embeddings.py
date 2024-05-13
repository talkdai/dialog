from langchain_openai import OpenAIEmbeddings

from dialog.settings import Settings

EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=Settings().OPENAI_API_KEY)