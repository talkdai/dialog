import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIChat(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    stream: bool = False


class OpenAIChoices(BaseModel):
    finish_reason: str = "stop"
    index: int = 0
    message: OpenAIMessage
    logprobs: Optional[str] = None


class OpenAIUsageDict(BaseModel):
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class OpenAIChatCompletion(BaseModel):
    choices: List[OpenAIChoices]
    created: float
    id: str
    model: str = "talkd-ai"
    object: str = "chat.completion"
    usage: OpenAIUsageDict


class OpenAIModel(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str


class OpenAIStreamChoice(BaseModel):
    index: int
    delta: dict
    logprobs: Optional[str] = None
    finish_reason: Optional[str] = None

class OpenAIStreamSchema(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int = int(datetime.datetime.now().timestamp())
    model: str = "talkd-ai"
    system_fingerprint: str = None
    choices: List[OpenAIStreamChoice]