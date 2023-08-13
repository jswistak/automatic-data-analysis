import openai
from os import getenv

openai.api_key = getenv("OPENAI_API_KEY")


def get_response(messages: list[dict]) -> dict:
    """Get completion from OpenAI GPT-3 API."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response
