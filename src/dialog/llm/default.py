import asyncio
import logging

from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)
from langchain_community.chat_models import ChatOpenAI

from dialog.learn.idf import categorize_conversation_history
from dialog.llm.abstract_llm import AbstractLLM
from dialog.llm.embeddings import get_most_relevant_contents_from_message
from dialog.llm.memory import generate_memory_instance
from dialog.settings import OPENAI_API_KEY, VERBOSE_LLM


class DialogLLM(AbstractLLM):
    @property
    def memory(self) -> BaseChatMemory:
        if self.session_id:
            return generate_memory_instance(
                session_id=self.session_id,
                parent_session_id=self.parent_session_id
            )
        return None

    def generate_prompt(self, input):
        relevant_contents = get_most_relevant_contents_from_message(input, top=1, dataset=self.dataset)

        if len(relevant_contents) == 0:
            prompt_templating = [
                SystemMessagePromptTemplate.from_template(self.config.get("prompt", {}).get("fallback")),
                HumanMessagePromptTemplate.from_template("{user_message}"),
            ]
            relevant_contents = []
        else:
            suggested_content = "Contexto: \n".join(
                [f"{c.question}\n{c.content}\n" for c in relevant_contents]
            )

            prompt_templating = [
                SystemMessagePromptTemplate.from_template(self.config.get("prompt").get("header")),
                MessagesPlaceholder(variable_name="chat_history"),
            ]

        if len(relevant_contents) > 0:
            suggested_message = self.config.get("prompt", {}).get('suggested')
            prompt_templating.append(
                SystemMessagePromptTemplate.from_template(
                    f"{suggested_message}. {suggested_content}"
                )
            )

        question_text = self.config.get("prompt").get("question_signalizer")
        prompt_templating.append(HumanMessagePromptTemplate.from_template(f"{question_text}" + ":\n{user_message}"))
        if VERBOSE_LLM:
            logging.info(f"Verbose LLM prompt: {prompt_templating}")
        self.prompt = ChatPromptTemplate(messages=prompt_templating)

    @property
    def llm(self) -> LLMChain:
        llm_config = self.config.get("model", {})
        conversation_options ={
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
                "k": self.config.get("memory_size", 5)
            }
            conversation_options["memory"] = ConversationBufferWindowMemory(
                **buffer_config
            )

        return LLMChain(**conversation_options)

    def postprocess(self, output: str) -> str:
        asyncio.create_task(categorize_conversation_history(self.memory))
        return output
