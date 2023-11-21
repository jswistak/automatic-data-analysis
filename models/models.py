from enum import Enum
from pydantic import BaseModel


class ConversationRolesEnum(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ConversationRolesInternalEnum(str, Enum):
    CODE = "code_generation"
    ANALYSIS = "analysis_suggestion_interpretation"


class Message(BaseModel):
    role: ConversationRolesEnum | ConversationRolesInternalEnum
    content: str

class LLMType(Enum):
    GPT4 = "gpt4"
    LLAMA2 = "llama2"