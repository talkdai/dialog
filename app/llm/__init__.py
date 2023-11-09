from langchain.chat_models import ChatOpenAI
from decouple import config

llm = ChatOpenAI(openai_api_key=config("OPENAI_API_KEY"))