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


def get_response(messages: list[dict]) -> dict:
    """Get completion from OpenAI GPT-3 API."""
    openai.api_key = getenv("OPENAI_API_KEY")

    # Add system message suffix to the local copy of the messages
    messages_local = messages.copy()
    if system_message_suffix is not None and len(messages_local) > 2:
        messages_local[-1:-1] = [
            {
                "role": ConversationRoles.SYSTEM,
                "content": system_message_suffix,
            }
        ]
    # TODO: Check for the maximum number of tokens

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_local,
    )
    return response
