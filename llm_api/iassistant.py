from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Union

from models.models import Message


class IAssistant(ABC):
    """
    Interface for a Large Language Model (LLM).
    It processes conversation contexts to generate response.
    """

    @abstractmethod
    def generate_response(
        self,
        conversation: List[Message],
    ) -> str:
        """
        Generate a response based on a conversation context and/or a specific message.

        Parameters:
        - conversation (List[dict]): A list of message objects representing the conversation history, where there may be multiple messages from the user and/or the system.

        Returns:
        str: The generated response from the LLM.
        """
        pass

    @abstractmethod
    def get_conversation_tokens(self, conversation: List[Message]) -> int:
        """
        Get tokens from a conversation.
        """
        pass
