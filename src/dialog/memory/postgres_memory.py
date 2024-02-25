from typing import List
from langchain.memory import PostgresChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables import run_in_executor

from dialog.settings import DATABASE_URL, PROJECT_CONFIG

LLM_MEMORY_SIZE = PROJECT_CONFIG.get("memory").get("memory_size")
class CustomPostgresChatMessageHistory(PostgresChatMessageHistory):
    """
    Custom wrapper of PostgresChatMessageHistory that allows custom functionalities.
    """

    def __init__(self, session_id: str):
        super().__init__(session_id=session_id, connection_string=DATABASE_URL)

    async def aget_messages(self, k: int = LLM_MEMORY_SIZE) -> List[BaseMessage]:
        """Async version of getting messages overwriting the parent method."""
        messages = await run_in_executor(None, lambda: self.messages)
        return messages[-k * 2 :] if k > 0 else []
