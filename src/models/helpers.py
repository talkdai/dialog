import uuid

from sqlalchemy import select

from models import Chat as ChatEntity
from models.db import session


def create_session(identifier = None):
    if identifier is None:
        session_uuid = uuid.uuid4().hex
    else:
        session_uuid = identifier

    instance = session.query(ChatEntity).filter_by(uuid=session_uuid).one()
    if instance is not None:
        return {"chat_id": instance.uuid}

    chat = ChatEntity(uuid=session_uuid)
    session.add(chat)
    session.commit()
    return {"chat_id": session_uuid}