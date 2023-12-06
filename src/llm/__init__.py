import asyncio
from typing import List

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)
from sqlalchemy import select

from learn.idf import categorize_conversation_history
from llm.memory import generate_memory_instance
from models import CompanyContent
from models.db import session
from settings import (LLM_CONFIG, MODEL_NAME, OPENAI_API_KEY, PROJECT_CONFIG,
                      PROMPT, VERBOSE_LLM)

CHAT_LLM = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=LLM_CONFIG.get("temperature"),
    model_name=MODEL_NAME,
)
EMBEDDINGS_LLM = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

FALLBACK_PROMPT = "Sorry, I don't understand. Can you rephrase that?"
fallback_config = PROJECT_CONFIG.get("fallback")
if fallback_config and fallback_config.get("prompt"):
    FALLBACK_PROMPT = PROJECT_CONFIG.get("fallback").get("prompt")


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
    possible_contents = session.scalars(
        select(CompanyContent)
        .filter(CompanyContent.embedding.l2_distance(message_embedding) < 5)
        .order_by(CompanyContent.embedding.l2_distance(message_embedding).asc())
        .limit(top)
    ).all()
    return possible_contents


def process_user_intent(session_id, message):
    """
    Process user intent using memory and embeddings
    """
    # top 2 most relevant contents
    relevant_contents = get_most_relevant_contents_from_message(message, top=2)

    if len(relevant_contents) == 0:
        prompt_templating = [
            SystemMessagePromptTemplate.from_template(FALLBACK_PROMPT),
            HumanMessagePromptTemplate.from_template("{user_message}"),
        ]
        relevant_contents = []
    else:
        suggested_content = "\n\n".join(
            [f"{c.question}\n{c.content}\n\n" for c in relevant_contents]
        )

        prompt_templating = [
            SystemMessagePromptTemplate.from_template(PROMPT.get("header")),
            MessagesPlaceholder(variable_name="chat_history"),
        ]

    # append prompt content subcategory
    if PROMPT.get("subcategory"):
        subprompt_subcategory = PROMPT.get("subcategory")
        for c in relevant_contents:
            if subprompt_subcategory.get(c.subcategory):
                subprompt = subprompt_subcategory.get(c.subcategory)
                prompt_templating.append(
                    SystemMessagePromptTemplate.from_template(
                        f"{subprompt.get('header')}\n\n"
                    )
                )

    # append prompt content suggestions
    if len(relevant_contents) > 0:
        prompt_templating.append(
            SystemMessagePromptTemplate.from_template(
                f"{PROMPT.get('suggested')}\n\n{suggested_content}"
            )
        )

    prompt_templating.append(HumanMessagePromptTemplate.from_template("{user_message}"))

    prompt = ChatPromptTemplate(messages=prompt_templating)

    conversation_options = {
        "llm": CHAT_LLM,
        "prompt": prompt,
        "verbose": VERBOSE_LLM
    }
    if PROMPT.get("memory", True):
        chat_memory = generate_memory_instance(session_id)
        buffer_memory = {
            "chat_memory": chat_memory,
            "memory_key": "chat_history",
            "return_messages": True,
            "k": PROMPT.get("memory_size", 5),
        }
        memory = ConversationBufferWindowMemory(**buffer_memory)
        conversation_options["memory"] = memory
    conversation = LLMChain(**conversation_options)
    ai_message = conversation(
        {
            "user_message": message,
        }
    )

    # categorize conversation history in background
    asyncio.create_task(categorize_conversation_history(chat_memory))
    return ai_message
