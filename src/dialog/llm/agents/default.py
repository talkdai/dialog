import asyncio
import logging

from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)
from langchain_openai.chat_models import ChatOpenAI

from dialog.learn.idf import categorize_conversation_history
from dialog_lib.agents.abstract import AbstractRAG
from dialog_lib.embeddings.generate import get_most_relevant_contents_from_message
from dialog_lib.db.memory import generate_memory_instance
from dialog.llm.embeddings import EMBEDDINGS_LLM
from dialog.settings import Settings
from dialog.db import get_session

class DialogLLM(AbstractRAG):
    def __init__(self, *args, **kwargs):
        kwargs["dbsession"] = next(get_session())
        super().__init__(*args, **kwargs)

    @property
    def memory(self) -> BaseChatMemory:
        if self.session_id:
            return generate_memory_instance(
                session_id=self.session_id,
                parent_session_id=self.parent_session_id,
                dbsession=self.dbsession,
                database_url=Settings().DATABASE_URL
            )
        return None

    def generate_prompt(self, text):
        self.relevant_contents = get_most_relevant_contents_from_message(
            text,
            top=Settings().LLM_RELEVANT_CONTENTS,
            dataset=self.dataset,
            session=self.dbsession,
            embeddings_llm=EMBEDDINGS_LLM,
            cosine_similarity_threshold=Settings().COSINE_SIMILARITY_THRESHOLD
        )
        prompt_config = self.config.get("prompt")
        fallback = prompt_config.get("fallback") or \
            self.config.get("fallback").get("prompt") # maintaining compatibility with the previous configuration
        header = prompt_config.get("header")
        suggested = prompt_config.get("suggested")
        messages = []
        if len(self.relevant_contents) > 0:
            context = "Context: \n".join(
                [f"{c.question}\n{c.content}\n" for c in self.relevant_contents]
            )
            messages.append(SystemMessagePromptTemplate.from_template(header))
            messages.append(SystemMessagePromptTemplate.from_template(
                f"{suggested}. {context}"))
            messages.append(
                MessagesPlaceholder(
                    variable_name="chat_history", optional=True))
            messages.append(
                HumanMessagePromptTemplate.from_template("{user_message}"))
        else:
            messages.append(
                SystemMessagePromptTemplate.from_template(fallback))
            messages.append(
                HumanMessagePromptTemplate.from_template("{user_message}"))
        self.prompt = ChatPromptTemplate.from_messages(messages)

        if Settings().VERBOSE_LLM:
            logging.info(f"Verbose LLM prompt: {self.prompt.pretty_print()}")

    @property
    def llm(self) -> LLMChain:
        llm_config = self.config.get("model", {})
        conversation_options = {
            "llm": ChatOpenAI(
                **llm_config,
                openai_api_key=self.llm_api_key or Settings().OPENAI_API_KEY
            ),
            "prompt": self.prompt,
            "verbose": self.config.get("verbose", False)
        }

        if self.memory:
            buffer_config = {
                "chat_memory": self.memory,
                "memory_key": "chat_history",
                "return_messages": True,
                "k": self.config.get("memory_size", Settings().LLM_MEMORY_SIZE)
            }
            conversation_options["memory"] = ConversationBufferWindowMemory(
                **buffer_config
            )

        return LLMChain(**conversation_options)

    def postprocess(self, output: str) -> str:
        if self.memory:
            asyncio.create_task(categorize_conversation_history(self.memory))
        return output
