from langchain_openai import ChatOpenAI

from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.prompts import format_document

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from dialog.settings import PROJECT_CONFIG
from dialog.vectorstores.pgvector import CustomPGVector

PROMPT_TEMPLATE = PROJECT_CONFIG.get("prompt").get("template")
CONTEXTUALIZE_HISTORY_PROMPT = PROJECT_CONFIG.get("prompt").get("contextualize_history")
MODEL_CONFIG = PROJECT_CONFIG.get("model", {})
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")
RETRIEVER_TOP_K = PROJECT_CONFIG.get("retriever").get("top_k")


def get_llm():
    return ChatOpenAI(**MODEL_CONFIG)


def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain():
    vectorstore = CustomPGVector()
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K})
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = get_llm()

    chain = (
        {"context": retriever | _combine_documents, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def get_contextualizer_chain():
    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_HISTORY_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    model = get_llm()
    return contextualize_prompt | model | StrOutputParser()


def get_rag_chain_with_memory():
    vectorstore = CustomPGVector()
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PROMPT_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    def contextualized_question(input: dict):
        if input.get("chat_history"):
            return get_contextualizer_chain()
        else:
            return input["question"]

    rag_chain = (
        RunnablePassthrough.assign(
            context=contextualized_question | retriever | format_docs
        )
        | prompt
        | llm
    )

    return rag_chain
