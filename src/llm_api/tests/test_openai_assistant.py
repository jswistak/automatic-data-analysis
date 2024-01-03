import pytest
from unittest.mock import patch, MagicMock
from llm_api.openai_assistant import OpenAIAssistant, _get_message_tokens


@pytest.mark.parametrize("message, expected_token_count", [
    ("Hello, world!", 4),
    ("", 0),
    (" ", 1),
])
def test_get_message_tokens(message, expected_token_count):
    assert _get_message_tokens(message) == expected_token_count


def test_get_conversation_tokens():
    conversation = [MagicMock(content="Hello"), MagicMock(content="world")]
    assistant = OpenAIAssistant("fake_api_key")
    token_count = assistant.get_conversation_tokens(conversation)
    assert token_count == 2
