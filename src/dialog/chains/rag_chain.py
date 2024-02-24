from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores.pgvector import PGVector

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.prompts import format_document

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from dialog.settings import COLLECTION_NAME, DATABASE_URL, PROJECT_CONFIG

PROMPT_TEMPLATE = PROJECT_CONFIG.get("prompt").get("template")
MODEL_CONFIG = PROJECT_CONFIG.get("model", {})
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")


def get_vector_store():
    return PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=DATABASE_URL,
        embedding_function=OpenAIEmbeddings(),
    )


def get_prompt():
    return ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


def get_model():
    return ChatOpenAI(**MODEL_CONFIG)


def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def get_rag_chain():
    vectorstore = get_vector_store()
    retriever = vectorstore.as_retriever()
    prompt = get_prompt()
    model = get_model()

    chain = (
        {"context": retriever | _combine_documents, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain
