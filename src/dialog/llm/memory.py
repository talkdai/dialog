from langchain.memory import PostgresChatMessageHistory
from langchain.schema.messages import BaseMessage, _message_to_dict

from dialog.models import Chat, ChatMessages
from dialog.models.db import get_session
from dialog.settings import Settings


class CustomPostgresChatMessageHistory(PostgresChatMessageHistory):
    """
    Custom chat message history for LLM
    """

    def __init__(self, *args, parent_session_id=None, dbsession=None, **kwargs):
        self.parent_session_id = parent_session_id
        self.dbsession = dbsession
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
        self.dbsession.query(Chat).where(Chat.uuid == self.session_id).update(
            {Chat.tags: tags}
        )
        self.dbsession.commit()

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in PostgreSQL"""
        message = ChatMessages(
            session_id=self.session_id, message=_message_to_dict(message)
        )
        if self.parent_session_id:
            message.parent = self.parent_session_id
        self.dbsession.add(message)
        self.dbsession.commit()


def generate_memory_instance(session_id, parent_session_id=None, dbsession=None):
    """
    Generate a memory instance for a given session_id
    """
    return CustomPostgresChatMessageHistory(
        connection_string=Settings().DATABASE_URL,
        session_id=session_id,
        parent_session_id=parent_session_id,
        table_name="chat_messages",
        dbsession=dbsession
    )


def add_user_message_to_message_history(session_id, message, memory=None, dbsession=None):
    """
    Add a user message to the message history and returns the updated
    memory instance
    """
    if not memory:
        memory = generate_memory_instance(session_id)

    memory.add_user_message(message)
    return memory


def get_messages(session_id, dbsession=None):
    """
    Get all messages for a given session_id
    """
    memory = generate_memory_instance(session_id, dbsession=dbsession)
    return memory.messages
