from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Union


class IAssistant(ABC):
    """
    Interface for a Large Language Model (LLM).
    It processes conversation contexts to generate response.
    """

    @abstractmethod
    def generate_response(
        self,
        conversation: List[dict] = None,
    ) -> str:
        """
        Generate a response based on a conversation context and/or a specific message.

        Parameters:
        - conversation (List[dict]): A list of message objects representing the conversation history, where there may be multiple messages from the user and/or the system.

        Returns:
        str: The generated response from the LLM.
        """
        pass
