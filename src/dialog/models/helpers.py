import uuid

from dialog.models import Chat as ChatEntity
from dialog.models.db import session


def create_session(identifier=None):
    if identifier is None:
        session_uuid = uuid.uuid4().hex

    chat = session.query(ChatEntity).filter_by(uuid=session_uuid).first()
    if chat:
        return {"chat_id": chat.uuid}

    chat = ChatEntity(uuid=session_uuid)
    session.add(chat)
    session.commit()

    return {"chat_id": session_uuid}
