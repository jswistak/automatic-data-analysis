from typing import List

from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from iassistant import IAssistant
from openai import OpenAI


def _get_response(response: ChatCompletion) -> str:
    """
    Get text response from the OpenAI API response.
    """
    if not response.choices or not response.choices[0].message.content:
        raise ValueError("Invalid response or text not found")
    return response.choices[0].message.content


class OpenAIAssistant(IAssistant):
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    def generate_response(
            self,
            conversation: List[ChatCompletionMessageParam],
    ) -> str:
        """
        Generate a response based on a conversation context and/or a specific message.

        Parameters:
        - conversation (List[dict]): A list of message objects representing the conversation history, where there may be multiple messages from the user and/or the system.

        Returns:
        str: The generated response from the LLM.
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
        )

        return _get_response(response)
