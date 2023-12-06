import uuid

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from models import Chat as ChatEntity
from models.db import session
from psycopg2.errors import UniqueViolation


def create_session(identifier = None):
    if identifier is None:
        session_uuid = uuid.uuid4().hex
    else:
        session_uuid = identifier

    try:
        instance = session.query(ChatEntity).filter_by(uuid=session_uuid).one()
    except NoResultFound:
        instance = None
    except UniqueViolation:
        return {"chat_id": session_uuid}

    if instance is not None:
        return {"chat_id": instance.uuid}

    chat = ChatEntity(uuid=session_uuid)
    session.add(chat)
    session.commit()
    return {"chat_id": session_uuid}