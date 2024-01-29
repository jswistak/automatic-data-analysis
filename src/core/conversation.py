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
        self.code_messages_missing_snippets: int = 0

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
        """Add message to the conversation."""
        self._conversation.append(Message(role=role, content=content))

    def _get_last_message(self) -> Message:
        """Get the last message in the conversation."""
        return self._conversation[-1]

    def _send_message_analysis(self) -> None:
        """
        Generates output from the analysis assistant and adds it to the conversation history.
        """
        analysis_conv = self._prompt.generate_conversation_context(
            self._conversation, ConversationRolesInternalEnum.ANALYSIS, LLMType.GPT4
        )
        analysis_response = self._analysis_assistant.generate_response(analysis_conv)
        self._add_to_conversation(
            ConversationRolesInternalEnum.ANALYSIS, analysis_response
        )
        self._runtime.add_description(analysis_response)

    def _execute_python_snippet(self, code: str) -> int:
        """Execute python code snippet in the runtime."""
        cell_idx = self._runtime.add_code(code)
        self._runtime.execute_cell(cell_idx)
        return cell_idx

    def _send_message_code(self) -> None:
        """
        Generates output from the code assistant and executes the code it generates.

        If the code assistant generates multiple code snippets, it executes them one by one.
        Output from each code snippet is stored in the conversation history and added to the report.
        In case snippet execution fails, the further execution is stopped.
        If traceback is longer than 20 lines, it is shortened to 20 lines.
        If plot was generated successfully, it is mentioned in the text output.
        """

        code_conv = self._prompt.generate_conversation_context(
            self._conversation, ConversationRolesInternalEnum.CODE, LLMType.GPT4
        )

        code_response = self._code_assistant.generate_response(
            code_conv,
            temperature=0.5,
        )
        code_snippets = self._extract_code_snippets_from_message(code_response)
        output = []
        first_snippet_idx = -1
        containsPythonSnippet = False
        for code_snippet in code_snippets:
            if not code_snippet.startswith("python"):
                continue  # Skip code snippets that are not in python
            containsPythonSnippet = True
            code = code_snippet[6:]  # Remove 'python' from the code snippet
            try:
                cell_idx = self._execute_python_snippet(code)
            except Exception as e:
                print("Error executing code snippet:\n")
                print(code)
                raise e

            if first_snippet_idx == -1:
                first_snippet_idx = cell_idx

            output.append(self._runtime.get_cell_output_stream(cell_idx))

            # Stop further code execution if the code snippet contains errors
            if output and ("Traceback" in output[-1] or "Error" in output[-1]):
                if "Traceback" in output[-1]:
                    pos = output[-1].find("Traceback")
                    traceback = output[-1][pos:].split("\n")
                    if len(traceback) > 20:
                        traceback = (
                            traceback[0] + "\n...\n" + "\n".join(traceback[-19:])
                        )
                        output[-1] = output[-1][:pos] + traceback

                break

            if self._runtime.check_if_plot_in_output(cell_idx):
                output[-1] += "\n\nPlot was generated successfully."
        if not containsPythonSnippet:
            self.code_messages_missing_snippets += 1

        if len(output) > 0:
            code_response = self.format_code_assistant_message(
                code_response, "\n".join(output)
            )

        if first_snippet_idx != -1:
            self._last_msg_first_cell_idx = first_snippet_idx

        self._add_to_conversation(
            role=ConversationRolesInternalEnum.CODE, content=code_response
        )

    def last_msg_contains_execution_errors(self) -> bool:
        """Check if the last step in the conversation contains errors."""
        last_message = self._get_last_message()
        if (
            last_message.role != ConversationRolesInternalEnum.CODE
            or "\n\nHere is the output of the provided code:\n```"
            not in last_message.content
        ):
            return False

        code_output = last_message.content.split(
            "\n\nHere is the output of the provided code:\n```"
        )[-1]
        if last_message.role == ConversationRolesInternalEnum.CODE and (
            "Traceback" in code_output or "Error" in code_output
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

        previous_msg_first_cell_idx = self._last_msg_first_cell_idx

        self.perform_next_step()

        # # Cleaning up previous code and fix request
        self._conversation.pop(-3)
        self._conversation.pop(-2)
        for _ in range(previous_msg_first_cell_idx, self._last_msg_first_cell_idx):
            self._runtime.remove_cell(previous_msg_first_cell_idx)

        self._last_msg_first_cell_idx = previous_msg_first_cell_idx

        return self._get_last_message()

    def get_conversation_json(self) -> str:
        """Get the conversation in json format."""
        return json.dumps([message.model_dump_json() for message in self._conversation])
