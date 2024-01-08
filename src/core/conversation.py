import json
from typing import List

from llm_api.iassistant import IAssistant
from models.models import ConversationRolesInternalEnum, LLMType, Message
from prompt_manager.ipromptmanager import IPromptManager
from runtime.iruntime import IRuntime
from core.utils import Colors, print_message


class Conversation:
    """Conversation class that handles the conversation flow and stores the conversation history."""

    def __init__(
        self,
        runtime: IRuntime,
        code_assistant: IAssistant,
        analysis_assistant: IAssistant,
        prompt: IPromptManager,
        conversation: List[Message] = None,
    ):
        self._conversation: List[Message] = conversation
        self._runtime: IRuntime = runtime
        self._code_assistant: IAssistant = code_assistant
        self._analysis_assistant: IAssistant = analysis_assistant
        self._prompt: IPromptManager = prompt

    @staticmethod
    def format_code_assistant_message(message: str, code_output: str) -> str:
        """Format the code assistant message."""
        return f"{message}\n\nHere is the output of the provided code:\n```{code_output}```"

    @staticmethod
    def _extract_code_snippets_from_message(message: str) -> list[str]:
        """Extract code snippets from message."""
        try:
            code_blocks = message.split("```")[1::2]
            return code_blocks
        except Exception as e:
            raise Exception("No code snippets found in response") from e

    def get_conversation(self) -> List[Message]:
        """Get the conversation."""
        return self._conversation

    def _add_to_conversation(
        self, role: ConversationRolesInternalEnum, content: str
    ) -> None:
        self._conversation.append(Message(role=role, content=content))

    def _get_last_message(self) -> Message:
        return self._conversation[-1]

    def _send_message_analysis(self) -> None:
        analysis_conv = self._prompt.generate_conversation_context(
            self._conversation, ConversationRolesInternalEnum.ANALYSIS, LLMType.GPT4
        )
        analysis_response = self._analysis_assistant.generate_response(analysis_conv)
        self._add_to_conversation(
            ConversationRolesInternalEnum.ANALYSIS, analysis_response
        )
        self._runtime.add_description(analysis_response)

    def _execute_python_snippet(self, code: str) -> int:
        cell_idx = self._runtime.add_code(code)
        self._runtime.execute_cell(cell_idx)
        return cell_idx

    def _send_message_code(self) -> None:
        code_conv = self._prompt.generate_conversation_context(
            self._conversation, ConversationRolesInternalEnum.CODE, LLMType.GPT4
        )

        code_response = self._code_assistant.generate_response(code_conv)
        code_snippets = self._extract_code_snippets_from_message(code_response)
        output = []

        for code_snippet in code_snippets:
            if not code_snippet.startswith("python"):
                continue  # Skip code snippets that are not in python

            code = code_snippet[6:]  # Remove 'python' from the code snippet
            cell_idx = self._execute_python_snippet(code)
            output.append(self._runtime.get_cell_output_stream(cell_idx))

            # Stop further code execution if the code snippet contains errors
            if output and ("Traceback" in output[-1] or "Error" in output[-1]):
                if "Traceback" in output[-1]:
                    last_output = output[-1].split("Traceback")
                    traceback = last_output[1].split("\n")
                    if len(traceback) > 20:
                        traceback = traceback[0] + "\n...\n" + "\n".join(traceback[-19:])
                        output[-1] = last_output[0] + "Traceback" + traceback

                break

            if self._runtime.check_if_plot_in_output(cell_idx):
                output[-1] += "\n\nPlot was generated successfully."

        if len(output) > 0:
            code_response = self.format_code_assistant_message(
                code_response, "\n".join(output)
            )

        self._add_to_conversation(
            role=ConversationRolesInternalEnum.CODE, content=code_response
        )

    def last_msg_contains_execution_errors(self) -> bool:
        """Check if the last step in the conversation contains errors."""
        last_message = self._get_last_message()
        if last_message.role == ConversationRolesInternalEnum.CODE and (
            "Traceback" in last_message.content or "Error" in last_message.content
        ):
            return True

        return False

    def perform_next_step(self) -> Message:
        """Perform the next step in the conversation."""
        # Generate response
        last_message = self._get_last_message()
        if last_message.role == ConversationRolesInternalEnum.CODE:
            self._send_message_analysis()
        elif last_message.role == ConversationRolesInternalEnum.ANALYSIS:
            self._send_message_code()
        else:
            raise Exception(f"Invalid conversation role: {last_message.role}")

        return self._get_last_message()

    def fix_last_code_message(self) -> Message:
        """
        Fix the last message in the conversation.
        Only code messages can be fixed.
        It impersonates the analysis assistant and sends the last message to the code assistant asking for a fix.
        """

        last_message = self._get_last_message()
        if last_message.role != ConversationRolesInternalEnum.CODE:
            raise Exception("Only code messages can be fixed")
        
        if not self.last_msg_contains_execution_errors():
            raise Exception("Last message does not contain errors")

        fix_request_msg = Message(
            role=ConversationRolesInternalEnum.ANALYSIS,
            content="Error during code execution occurred. Please fix it.",
        )

        self._conversation.append(fix_request_msg)
        print_message(fix_request_msg, Colors.BLUE)

        self.perform_next_step()

        # # Cleaning up previous code and fix request
        # self._conversation.pop(-3)
        # self._conversation.pop(-2)
        # self._runtime.remove_cell(-3)
        # self._runtime.remove_cell(-2)

        return self._get_last_message()

    def get_conversation_json(self) -> str:
        """Get the conversation in json format."""
        return json.dumps([message.model_dump_json() for message in self._conversation])
