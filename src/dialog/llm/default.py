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
from dialog.llm.abstract_llm import AbstractLLM
from dialog.llm.embeddings import get_most_relevant_contents_from_message
from dialog.llm.memory import generate_memory_instance
from dialog.settings import (LLM_MEMORY_SIZE, LLM_RELEVANT_CONTENTS,
                             OPENAI_API_KEY, VERBOSE_LLM, FALLBACK_NOT_FOUND_RELEVANT_CONTENTS)


class DialogLLM(AbstractLLM):
    @property
    def memory(self) -> BaseChatMemory:
        if self.session_id:
            return generate_memory_instance(
                session_id=self.session_id,
                parent_session_id=self.parent_session_id
            )
        return None

    def generate_prompt(self, text):
        self.relevant_contents = get_most_relevant_contents_from_message(
            text, top=LLM_RELEVANT_CONTENTS, dataset=self.dataset)
        prompt_config = self.config.get("prompt")
        fallback = self.config.get("fallback").get("prompt")
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
            messages.append(MessagesPlaceholder(variable_name="chat_history",
            optional=True))
            messages.append(
                HumanMessagePromptTemplate.from_template("{user_message}"))
        else:
            messages.append(
                SystemMessagePromptTemplate.from_template(fallback))
            messages.append(
                HumanMessagePromptTemplate.from_template("{user_message}"))

        if not FALLBACK_NOT_FOUND_RELEVANT_CONTENTS:
            self.prompt = ChatPromptTemplate.from_messages(messages)
        if VERBOSE_LLM:
            logging.info(f"Verbose LLM prompt: {self.prompt.pretty_print()}")

    @property
    def llm(self) -> LLMChain:
        llm_config = self.config.get("model", {})
        conversation_options = {
            "llm": ChatOpenAI(
                **llm_config,
                openai_api_key=self.llm_key or OPENAI_API_KEY
            ),
            "prompt": self.prompt,
            "verbose": self.config.get("verbose", False)
        }

        if self.memory:
            buffer_config = {
                "chat_memory": self.memory,
                "memory_key": "chat_history",
                "return_messages": True,
                "k": self.config.get("memory_size", LLM_MEMORY_SIZE)
            }
            conversation_options["memory"] = ConversationBufferWindowMemory(
                **buffer_config
            )

        return LLMChain(**conversation_options)

    def postprocess(self, output: str) -> str:
        if self.memory:
            asyncio.create_task(categorize_conversation_history(self.memory))
        return output
