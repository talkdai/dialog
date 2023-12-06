import requests
import logging

from fastapi import HTTPException

from llm import process_user_intent
from settings import WHATSAPP_VERIFY_TOKEN, WHATSAPP_API_TOKEN, WHATSAPP_ACCOUNT_NUMBER

from models.helpers import create_session

from webhooks.serializers import *

logger = logging.getLogger(__name__)


async def whatsapp_get_response(request):
    """
    Returns the challenge response for WhatsApp if verify token matches
    the one available in settings, else returns None
    """
    if request.query_params.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
        return int(request.query_params.get("hub.challenge"))

    raise HTTPException(status_code=404)


async def whatsapp_post_response(request, body):
    value = body["entry"][0]["changes"][0]["value"]
    try:
        message = value["messages"][0]["text"]["body"]
    except KeyError:
        raise HTTPException(status_code=200)

    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    logger.info(value)
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_ACCOUNT_NUMBER}/messages"

    create_session(identifier=from_number)

    processed_message = await process_user_intent(from_number, message)
    processed_message = processed_message["text"]
    logger.info("Processed message: %s", processed_message)

    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": processed_message},
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code not in [200, 201]:
        logger.info(f"Failed request: {response.text}")

    response.raise_for_status()
    return {"status": "success"}