from abc import ABC, abstractmethod
from enum import Enum
from models.models import LLMType, ConversationRolesInternalEnum, Message


class IPromptManager(ABC):
    """
    Interface for a Prompt Manager.
    It generates specific prompts for a given Agent (Code Generation or Analysis Suggestion and Interpretation) based on the current conversation and the LLM type.
    """

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
        match agent_type:
            case ConversationRolesInternalEnum.CODE:
                return self._generate_code_generation_prompt(conversation, llm_type)
            case ConversationRolesInternalEnum.ANALYSIS:
                return self._generate_analysis_suggestion_interpretation_prompt(
                    conversation, llm_type
                )
            case _:
                raise NotImplementedError(f"Agent type {agent_type} not implemented.")

    def _change_roles(
        self, conversation: list[Message], roles_dict: object, limit: int = 5
    ) -> list[Message]:
        """
        Change the roles of the messages in the conversation, based on a dictionary.
        """
        llm_conversation = []
        for message in conversation[:limit]:
            msg = message.model_copy()
            try:
                msg.role = roles_dict[msg.role]
            except KeyError:
                raise NotImplementedError(
                    f"Conversation role {message.role} not implemented."
                )
            llm_conversation.append(msg)
        return llm_conversation

    @abstractmethod
    def _generate_code_generation_prompt(
        self, conversation: list[Message], llm_type: LLMType
    ) -> list[Message]:
        """
        Generate a prompt for a code generation agent based on the current conversation.

        Parameters:
        - conversation (List[dict]): The current conversation context.
        - llm_type (LLMType): The type of Large Language Model.

        Returns:
        List[dict]: The generated conversation context. To be used as input for the LLM.
        """
        raise NotImplementedError

    @abstractmethod
    def _generate_analysis_suggestion_interpretation_prompt(
        self, conversation: list[Message], llm_type: LLMType
    ) -> list[Message]:
        """
        Generate a prompt for a code generation agent based on the current conversation.

        Parameters:
        - conversation (List[dict]): The current conversation context.
        - llm_type (LLMType): The type of Large Language Model.

        Returns:
        List[dict]: The generated conversation context. To be used as input for the LLM.
        """
        raise NotImplementedError
