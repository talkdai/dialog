import uuid

from dialog.models import Chat as ChatEntity
from dialog.models.db import get_session


def create_session(identifier=None, dbsession=None):
    if not dbsession:
        dbsession = next(get_session())

    if identifier is None:
        identifier = uuid.uuid4().hex

    chat = dbsession.query(ChatEntity).filter_by(session_id=identifier).first()
    if not chat:
        chat = ChatEntity(session_id=identifier)
        dbsession.add(chat)
        dbsession.commit()

    return {"chat_id": chat.session_id}
