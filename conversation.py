import json
from completion import get_response


class ConversationRoles:
    """OpenAI GPT API roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Conversation:
    """Conversation class that handles the conversation flow and stores the conversation history."""

    @staticmethod
    def extract_message_from_response(response: dict) -> dict:
        """Extract the message from GPT completion."""
        try:
            return response.choices[0]["message"]["content"]
        except Exception as e:
            raise Exception("Response format incorrect") from e

    @staticmethod
    def extract_code_snippets_from_message(message: str) -> list[str]:
        """Extract code snippets from message."""
        try:
            code_blocks = message.split("```")[1::2]
            return code_blocks
        except Exception as e:
            raise Exception("No code snippets found in response") from e

    def __init__(self, conversation: list = None, python_code_executed: str = None):
        self.conversation = conversation
        self.python_code_executed = python_code_executed
        self.last_response = None

    def _add_to_conversation(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def add_executed_code(self, code: str) -> None:
        """Add executed code to the conversation history."""
        self.python_code_executed += code + "\n"

    def generate_response(
        self, conversation_role: ConversationRoles = None, message_content: str = None
    ) -> str:
        """Generate a GPT response and add it to the conversation history."""
        if message_content is not None:
            if conversation_role not in [
                ConversationRoles.USER,
                ConversationRoles.SYSTEM,
            ]:
                raise Exception(
                    "Only user and system can add messages to the conversation"
                )
            self._add_to_conversation(conversation_role, message_content)

        self.last_response = get_response(self.conversation)
        message = Conversation.extract_message_from_response(self.last_response)
        self._add_to_conversation(ConversationRoles.ASSISTANT, message)

        return message

    def generate_response_with_snippets(
        self, conversation_role: ConversationRoles, message_content: str = None
    ) -> tuple[str, list[str]]:
        """
        Generate a GPT response and add it to the conversation history.
        Return the response with captured code snippets.
        """
        message = self.generate_response(conversation_role, message_content)
        code_snippets: list[str] = Conversation.extract_code_snippets_from_message(
            message
        )
        return message, code_snippets

    def save_conversation_to_file(self) -> None:
        """Save the conversation history to a file."""
        print("Saving conversation...")
        # Retrieve the latest conversation number
        number_file_path = "latest_conversation_number.txt"
        try:
            with open(number_file_path, "r") as number_file:
                latest_conversation_number = int(number_file.read())
        except FileNotFoundError:
            latest_conversation_number = 1

        conversation_path = (
            f"conversations/conversation{latest_conversation_number:04d}.json"
        )
        with open(conversation_path, "w") as f:
            json.dump(self.conversation, f)

        if self.python_code_executed is not None:
            code_path = f"conversations/conversation{latest_conversation_number:04d}.py"
            with open(code_path, "w") as f:
                f.write(self.python_code_executed)

        latest_conversation_number += 1
        with open(number_file_path, "w") as number_file:
            number_file.write(str(latest_conversation_number))

        print("Conversation saved to", conversation_path)
