from typing import List
from decouple import config

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import PostgresChatMessageHistory, ConversationBufferMemory

from sqlalchemy import select

from app.models.db import session, url
from app.models import Chat, CompanyContent

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

DB_URL = "postgresql://{username}:{password}@{host}:{port}/{database}".format(
    username=config("PSQL_USER"),
    password=config("PSQL_PASSWORD"),
    host=config("PSQL_HOST", default="localhost"),
    database=config("PSQL_DATABASE", default="talkdai"),
    port=config("PSQL_PORT", default="5432")
)

CHAT_LLM = ChatOpenAI(openai_api_key=config("OPENAI_API_KEY"))
EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=config("OPENAI_API_KEY"))


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

def get_most_relevant_contents_from_message(message, top=5):
    message_embedding = generate_embedding(message)
    possible_contents = session.scalars(select(CompanyContent).order_by(
        CompanyContent.embedding.l2_distance(message_embedding)
    ).limit(top))
    return possible_contents

def generate_memory_instance(session_id):
    """
    Generate a memory instance for a given session_id
    """
    return PostgresChatMessageHistory(
        connection_string=DB_URL,
        session_id=session_id,
        table_name="chat_messages"
    )

def add_user_message_to_message_history(
        session_id, message, memory=None
):
    """
    Add a user message to the message history and returns the updated
    memory instance
    """
    if not memory:
        memory = generate_memory_instance(session_id)

    memory.add_user_message(message)
    return memory

def get_messages(session_id):
    """
    Get all messages for a given session_id
    """
    memory = generate_memory_instance(session_id)
    return memory.messages

def process_user_intent(
        session_id, message
):
    """
    Process user intent using memory and embeddings
    """
    relevant_contents = get_most_relevant_contents_from_message(message)

    # TODO: Alter prompt to come from the database
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                "You are a nice chatbot having a conversation with a human."
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{user_message}")
        ]
    )


    psql_memory = generate_memory_instance(session_id)
    memory = ConversationBufferMemory(
        memory_key="chat_history", chat_memory=psql_memory
    )
    conversation = LLMChain(
        llm=CHAT_LLM,
        prompt=prompt,
        # memory=memory,
        verbose=True
    )
    ai_message = conversation({
        "user_message": message,
        "chat_history": psql_memory.messages
    })
    psql_memory.add_user_message(message)
    psql_memory.add_ai_message(ai_message["text"])

    return ai_message
