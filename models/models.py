from enum import Enum
from pydantic import BaseModel


class ConversationRolesEnum(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    role: ConversationRolesEnum
    content: str