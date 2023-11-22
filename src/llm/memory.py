
from langchain.memory import PostgresChatMessageHistory
from langchain.schema.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    _message_to_dict,
)
from models import Chat, ChatMessages
from models.db import session
from settings import DATABASE_URL


class CustomPostgresChatMessageHistory(PostgresChatMessageHistory):
    """
    Custom chat message history for LLM
    """
    def __init__(self, *args, parent_session_id=None, **kwargs):
        self.parent_session_id = parent_session_id
        super().__init__(*args, **kwargs)

    def _create_table_if_not_exists(self) -> None:
        """
        create table if it does not exist
        add a new column for timestamp
        """
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            message JSONB NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );"""
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def add_tags(self, tags: str) -> None:
        """Add tags for a given session_id/uuid on chats table"""
        session.query(Chat).where(Chat.uuid == self.session_id).update({Chat.tags: tags})
        session.commit()

    def add_message(self, message: BaseMessage) -> ChatMessages:
        """Append the message to the record in PostgreSQL"""
        message = ChatMessages(session_id=self.session_id, message=_message_to_dict(message))
        if self.parent_session_id:
            message.parent = self.parent_session_id
        session.add(message)
        session.commit()


def generate_memory_instance(session_id, parent_session_id=None):
    """
    Generate a memory instance for a given session_id
    """
    return CustomPostgresChatMessageHistory(
        connection_string=DATABASE_URL,
        session_id=session_id,
        parent_session_id=parent_session_id,
        table_name="chat_messages"
    )


def add_user_message_to_message_history(session_id, message, memory=None):
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
