import asyncio
import logging

from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnablePassthrough
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain_openai.chat_models import ChatOpenAI

from dialog.learn.idf import categorize_conversation_history
from dialog.llm.abstract_llm import AbstractLLM
from dialog.llm.embeddings import get_most_relevant_contents_from_message
from dialog.llm.memory import generate_memory_instance, get_messages
from dialog.settings import Settings

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class DialogLcelLLM(AbstractLLM):
    parser = StrOutputParser()

    @property
    def memory(self) -> BaseChatMemory:
        if self.session_id:
            return generate_memory_instance(
                session_id=self.session_id,
                parent_session_id=self.parent_session_id,
                dbsession=self.dbsession
            )
        return None

    def generate_prompt(self, text):
        self.relevant_contents = get_most_relevant_contents_from_message(
            text,
            top=Settings().LLM_RELEVANT_CONTENTS,
            dataset=self.dataset,
            session=self.dbsession
        )
        prompt_config = self.config.get("prompt")
        fallback = prompt_config.get("fallback") or self.config.get("fallback").get("prompt") # maintaining compatibility with the previous configuration
        header = prompt_config.get("header")
        suggested = prompt_config.get("suggested")
        if len(self.relevant_contents) > 0:
            context = "Context: \n".join(
                [f"{c.question}\n{c.content}\n" for c in self.relevant_contents]
            )
            self.prompt = ChatPromptTemplate.from_template(
                "\n".join([
                    header,
                    suggested,
                    context,
                    "{user_message}"
                ])
            )
        else:
            self.prompt = ChatPromptTemplate.from_template(
                "\n".join([
                    fallback,
                    "{user_message}"
                ])
            )

        if Settings().VERBOSE_LLM:
            logging.info(f"Verbose LLM prompt: {self.prompt.pretty_print()}")

    @property
    def llm(self) -> LLMChain:
        llm_config = self.config.get("model", {})
        conversation_options = {
            "llm": ChatOpenAI(
                **llm_config,
                openai_api_key=self.llm_key or Settings().OPENAI_API_KEY
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

    def process(self, input):
        processed_input = self.preprocess(input)
        self.generate_prompt(processed_input)
        chain = self.prompt | self.llm
        output = chain.invoke({
            "user_message": processed_input
        })
        return self.postprocess(output)