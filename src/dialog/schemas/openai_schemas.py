from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIChat(BaseModel):
    model: str
    messages: List[OpenAIMessage]


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
    model: str = "talkdai"
    object: str = "chat.completion"
    usage: OpenAIUsageDict


class OpenAIModel(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str