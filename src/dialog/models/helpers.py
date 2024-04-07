import uuid

from dialog.models import Chat as ChatEntity
from dialog.models.db import get_session


def create_session(identifier=None, dbsession=None):
    if identifier is None:
        identifier = uuid.uuid4().hex

    chat = dbsession.query(ChatEntity).filter_by(uuid=identifier).first()
    if not chat:
        chat = ChatEntity(uuid=identifier)
        dbsession.add(chat)
        dbsession.commit()

    return {"chat_id": chat.uuid}
