import openai
from os import getenv


class ConversationRoles:
    """OpenAI GPT API roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


# openai.api_key = getenv("OPENAI_API_KEY")
# print("OpenAI API key has been set")


def get_response(messages: list[dict], system_message_suffix: str = None) -> dict:
    """Get completion from OpenAI GPT-3 API."""
    openai.api_key = getenv("OPENAI_API_KEY")
    if system_message_suffix is not None:
        messages.append(
            {
                "role": ConversationRoles.SYSTEM,
                "content": system_message_suffix,
            }
        )
    print(messages)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response
