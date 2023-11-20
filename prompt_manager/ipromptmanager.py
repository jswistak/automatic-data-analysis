from abc import ABC, abstractmethod
from enum import Enum
from models.models import LLMType, ConversationRolesInternalEnum, Message


class IPromptManager(ABC):
    """
    Interface for a Prompt Manager.
    It generates specific prompts for a given Agent (Code Generation or Analysis Suggestion and Interpretation) based on the current conversation and the LLM type.
    """

    @abstractmethod
    def generate_conversation_context(
        self,
        conversation: list[Message],
        agent_type: ConversationRolesInternalEnum,
        llm_type: LLMType,
    ) -> list[Message]:
        """
        Generate a prompt for a specific agent and LLM type based on the current conversation.

        Parameters:
        - conversation (List[dict]): The current conversation context.
        - agent_type (AgentType): The type of agent.
        - llm_type (LLMType): The type of Large Language Model.

        Returns:
        List[dict]: The generated conversation context. To be used as input for the LLM.
        """
        pass
