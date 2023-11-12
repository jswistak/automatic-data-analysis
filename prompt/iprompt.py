from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Union
from enum import Enum


class IPrompt(ABC):
    """
    Interface for Prompt Manager
    It takes a current conversation and generates specific conversation with a specific system prompt for an given Agent (Code Generation or Analysis Suggestion and Interpretation).
    """


class AgentType(Enum):
    CODE_GENERATION = 1
    ANALYSIS_SUGGESTION_INTERPRETATION = 2


class LLMType(Enum):
    GPT4 = 1
    LLAMA2 = 2


class IPrompt(ABC):
    """
    Interface for a Prompt Manager.
    It generates specific prompts for a given Agent (Code Generation or Analysis Suggestion and Interpretation) based on the current conversation and the LLM type.
    """

    @abstractmethod
    def generate_conversation_context(
        self,
        conversation: List[dict],
        agent_type: AgentType,
        llm_type: LLMType,
    ) -> List[dict]:
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
