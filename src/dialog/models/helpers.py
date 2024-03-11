import uuid

from dialog.models import Chat as ChatEntity
from dialog.models.db import session_scope


def create_session(identifier=None):
    if identifier is None:
        identifier = uuid.uuid4().hex

    with session_scope() as session:
        chat = session.query(ChatEntity).filter_by(uuid=identifier).first()
        if not chat:
            chat = ChatEntity(uuid=identifier)
            session.add(chat)

    return {"chat_id": chat.uuid}
