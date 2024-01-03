import unittest
from models.models import ConversationRolesEnum, ConversationRolesInternalEnum, Message, LLMType


class TestMessageModel(unittest.TestCase):
    def test_message_creation(self):
        # Test creating a Message instance
        message = Message(role=ConversationRolesEnum.USER, content="Hello!")
        self.assertIsInstance(message, Message)
        self.assertEqual(message.role, ConversationRolesEnum.USER)
        self.assertEqual(message.content, "Hello!")
        self.assertIsInstance(message.role, ConversationRolesEnum)
        self.assertEqual(message.role, ConversationRolesEnum.USER)

    def test_llm_type_enum(self):
        # Test LLMType enum values
        self.assertEqual(LLMType.GPT4.value, "gpt4")
        self.assertEqual(LLMType.LLAMA2.value, "llama2")

    def test_conversation_roles_enum(self):
        # Test ConversationRolesEnum enum values
        self.assertEqual(ConversationRolesEnum.SYSTEM.value, "system")
        self.assertEqual(ConversationRolesEnum.USER.value, "user")
        self.assertEqual(ConversationRolesEnum.ASSISTANT.value, "assistant")
        self.assertEqual(ConversationRolesEnum.FUNCTION.value, "function")

    def test_conversation_roles_internal_enum(self):
        # Test ConversationRolesInternalEnum enum values
        self.assertEqual(ConversationRolesInternalEnum.CODE.value, "code_generation")
        self.assertEqual(ConversationRolesInternalEnum.ANALYSIS.value, "analysis_suggestion_interpretation")

