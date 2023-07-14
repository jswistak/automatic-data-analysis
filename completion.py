import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_response(messages: list[dict])  -> dict:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response

def extract_code_snippets_from_response(response: dict) -> list[str]:
    try:
        code_blocks = extract_message_from_response(response).split("```")[1::2]
        return code_blocks
    except Exception as e:
        raise Exception("No code snippets found in response") from e

def extract_message_from_response(response: dict) -> dict:
    try:
        return response.choices[0]["message"]["content"]
    except Exception as e:
        raise Exception("Response format incorrect") from e

