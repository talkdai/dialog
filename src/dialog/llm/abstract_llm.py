from typing import List, Dict

from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import ChatPromptTemplate

class AbstractLLM:
    def __init__(self, config, session_id=None, parent_session_id=None, dataset=None, llm_key=None):
        """
        :param config: Configuration dictionary

        The constructor of the AbstractLLM class allows users to pass
        a configuration dictionary to the LLM. This configuration dictionary
        can be used to configure the LLM temperature, prompt and other
        necessities.
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")

        self.config = config
        self.prompt = None
        self.session_id = session_id 
        self.dataset = dataset
        self.llm_key = llm_key
        self.parent_session_id = parent_session_id

    def get_prompt(self, input) -> ChatPromptTemplate:
        """
        Function that generates the prompt for the LLM.
        """
        raise NotImplementedError("Prompt must be implemented")

    @property
    def memory(self) -> BaseChatMemory:
        """
        Returns the memory instance
        """
        raise NotImplementedError("Memory must be implemented")

    @property
    def llm(self) -> LLMChain:
        """
        Returns the LLM instance. If a memory instance is provided,
        the LLM instance should be initialized with the memory instance.

        If no memory instance is provided, the LLM instance should be
        initialized without a memory instance.
        """
        raise NotImplementedError("LLM must be implemented")

    def preprocess(self, input: str) -> str:
        """
        Function that pre-process the LLM input, enabling users
        to modify the input before it is processed by the LLM.

        This can be used to add context or prefixes to the LLM.
        """
        return input

    def generate_prompt(self, input: str) -> str:
        """
        Function that generates the prompt using PromptTemplate for the LLM.
        """
        return input

    def postprocess(self, output: str) -> str:
        """
        Function that post-process the LLM output, enabling users
        to modify the output before it is returned to the user.
        """
        return output

    def process(self, input: str):
        """
        Function that encapsulates the pre-processing, processing and post-processing
        of the LLM.
        """
        fallback = self.config.get("fallback", "I'm sorry, I didn't understand your question. Could you rephrase it?")
        processed_input = self.preprocess(input)
        self.generate_prompt(processed_input)
        if len(self.prompt.messages) == 0:
            return {"text": fallback}
        output = self.llm.invoke({
            "user_message": processed_input,
        })
        processed_output = self.postprocess(output)
        return processed_output
