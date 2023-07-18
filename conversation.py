import json
from completion import (
    get_response,
)
from utils import Colors


class Conversation:
    @staticmethod
    def extract_message_from_response(response: dict) -> dict:
        try:
            return response.choices[0]["message"]["content"]
        except Exception as e:
            raise Exception("Response format incorrect") from e

    @staticmethod
    def extract_code_snippets_from_message(message: str) -> list[str]:
        try:
            code_blocks = message.split("```")[1::2]
            return code_blocks
        except Exception as e:
            raise Exception("No code snippets found in response") from e

    @staticmethod
    def extract_code_snippets_from_response(response: dict) -> list[str]:
        try:
            code_blocks = Conversation.extract_message_from_response(response).split(
                "```"
            )[1::2]
            return code_blocks
        except Exception as e:
            raise Exception("No code snippets found in response") from e

    def __init__(self, conversation: list = None, python_code_executed: str = None):
        self.conversation = conversation
        self.python_code_executed = python_code_executed
        self.last_response = None

    def _add_to_conversation(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def generate_response(self, conversation_message: dict = None) -> str:
        if conversation_message is not None:
            self._add_to_conversation(
                role=conversation_message["role"],
                content=conversation_message["content"],
            )
            print(
                f"{Colors.BOLD_GREEN}User message:{Colors.END}\n",
                f"{Colors.GREEN}",
                conversation_message["content"],
                f"{Colors.END}",
            )
        self.last_response = get_response(self.conversation)
        message = Conversation.extract_message_from_response(self.last_response)
        self._add_to_conversation(
            role="assistant",
            content=message,
        )
        return message

    def save_conversation_to_file(self) -> None:
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
