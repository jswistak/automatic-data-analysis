from abc import ABC, abstractmethod

from models.models import Message


class IAssistant(ABC):
    """
    Interface for a Large Language Model (LLM).
    It processes conversation contexts to generate response.
    """

    @abstractmethod
    def generate_response(
        self,
        conversation: list[Message],
        temperature: float = 1.0,
        top_p: float = 1.0,
    ) -> str:
        """
        Generate a response based on a conversation context and/or a specific message.

        Parameters:
        - conversation (List[dict]): A list of message objects representing the conversation history, where there may be multiple messages from the user and/or the system.
        - temperature (float): The temperature parameter for the LLM.
        - top_p (float): The top-p parameter for the LLM.

        Returns:
        str: The generated response from the LLM.
        """
        pass

    @abstractmethod
    def get_conversation_tokens(self, conversation: list[Message]) -> int:
        """
        Get tokens from a conversation.
        """
        pass
