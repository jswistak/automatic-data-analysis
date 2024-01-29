from enum import Enum

from pydantic import BaseModel


class ConversationRolesEnum(str, Enum):
    """Conversation roles for the LLM API."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ConversationRolesInternalEnum(str, Enum):
    """Conversation roles for the internal usage."""

    CODE = "code_generation"
    ANALYSIS = "analysis_suggestion_interpretation"


class Message(BaseModel):
    """Messages are the basic building blocks of a conversation."""

    role: ConversationRolesEnum | ConversationRolesInternalEnum
    content: str


class LLMType(Enum):
    """The type of LLM to use."""

    GPT4 = "gpt4"
    LLAMA2 = "llama2"
