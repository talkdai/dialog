import requests
import logging

from fastapi import HTTPException

from llm import process_user_intent
from settings import WHATSAPP_VERIFY_TOKEN, WHATSAPP_API_TOKEN

from models.helpers import create_session

from webhooks.serializers import *

logger = logging.getLogger(__name__)


def whatsapp_get_response(request):
    """
    Returns the challenge response for WhatsApp if verify token matches
    the one available in settings, else returns None
    """
    if request.query_params.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
        return int(request.query_params.get("hub.challenge"))

    raise HTTPException(status_code=404)


def whatsapp_post_response(request, body):
    value = body["entry"][0]["changes"][0]["value"]
    try:
        message = value["messages"][0]["text"]["body"]
    except KeyError:
        logger.error(f"Message body not found in request, {body}")
        raise HTTPException(status_code=400)

    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://graph.facebook.com/v15.0/{phone_number_id}/messages"


    create_session(identifier=from_number)

    processed_message = process_user_intent(from_number, message)["text"]
    logger.info("Processed message: %s", processed_message)

    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": processed_message},
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return {"status": "success"}