import pytest
from unittest.mock import MagicMock
from prompt_manager.few_shot import FewShot, ConversationRolesInternalEnum, ConversationRolesEnum, LLMType, Message, \
    CODE_GENERATION_PROMPT, ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT
from unittest.mock import patch

# Mocking the Message class
mock_message = MagicMock(spec=Message)


@pytest.fixture
def fewshot_instance():
    return FewShot()


@pytest.mark.parametrize("conversation", [
    [Message(role=ConversationRolesInternalEnum.CODE, content="Sample message")],
    [Message(role=ConversationRolesInternalEnum.ANALYSIS, content="Sample message")]
])
@pytest.mark.parametrize("agent", [
    (ConversationRolesInternalEnum.CODE, CODE_GENERATION_PROMPT),
    (ConversationRolesInternalEnum.ANALYSIS, ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT)
])
def test_generate_conversation_context(fewshot_instance, conversation, agent):
    agent_type, expected_prompt = agent
    result = fewshot_instance.generate_conversation_context(
        conversation=conversation,
        agent_type=agent_type,
        llm_type=LLMType.GPT4
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].role == ConversationRolesEnum.SYSTEM
    assert result[0].content == expected_prompt


@pytest.mark.parametrize("conversation", [
    [Message(role=ConversationRolesInternalEnum.CODE, content="Sample message")]
])
def test_generate_conversation_context_not_implemented(fewshot_instance, conversation):
    with pytest.raises(NotImplementedError):
        fewshot_instance.generate_conversation_context(
            conversation=conversation,
            agent_type="invalid_agent_type",  # This should be an invalid agent type
            llm_type=LLMType.GPT4
        )
