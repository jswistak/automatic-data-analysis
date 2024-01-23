from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai import BadRequestError
from llm_api.utils import together
from llm_api.iassistant import IAssistant

MODEL_NAME = "togethercomputer/CodeLlama-34b-Python"


def _get_response(response: ChatCompletion) -> str:
    """
    Get text response from the OpenAI API response.
    """
    if not response.choices or not response.choices[0].message.content:
        print(response)
        raise ValueError("Invalid response or text not found")
    return response.choices[0].message.content


class LLaMA2CodeAssistant(IAssistant):
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz",
        )
        together.api_key = api_key

    def generate_response(
        self,
        conversation: list[ChatCompletionMessageParam],
        temperature: float = 1.0,
        top_p: float = 1.0,
    ) -> str:
        """
        Generate a response based on a conversation context and/or a specific message.

        Parameters:
        - conversation (list[dict]): A list of message objects representing the conversation history, where there may be multiple messages from the user and/or the system.

        Returns:
        str: The generated response from the LLM.
        """

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            temperature=temperature,
            top_p=top_p,
        )
        return _get_response(response)

    def get_conversation_tokens(
        self, conversation: list[ChatCompletionMessageParam]
    ) -> int:
        """
        Get tokens from a conversation.
        """
        raise NotImplementedError("Not implemented yet")
