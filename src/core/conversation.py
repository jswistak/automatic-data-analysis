import json
from typing import List, Tuple

from llm_api.iassistant import IAssistant
from models.models import ConversationRolesInternalEnum, LLMType, Message
from prompt_manager.ipromptmanager import IPromptManager
from runtime.iruntime import IRuntime


class CodeRetryLimitExceeded(Exception):
    """Exception raised when too many errors occur during code execution."""

    def __init__(self, message="Exceeded code retry limit"):
        self.message = message
        super().__init__(self.message)


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
        return f"{message}\n\nHere is the output of the following code:\n```{code_output}```"

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
            if code_snippet.startswith("python"):
                code = code_snippet[6:]
                cell_idx = self._execute_python_snippet(code)
                output.append(self._runtime.get_cell_output_stream(cell_idx))

                # stop execution if error
                if output[-1].startswith("Traceback"):
                    if len(output[-1].split("\n")) > 10:
                        output[-1] = "Traceback:\n...\n" + "\n".join(output[-1].split("\n")[-9:])
                    break

                if self._runtime.check_if_plot_in_output(cell_idx):
                    output[
                        -1
                    ] = "Plot generated, but cannot be interpreted in a text format."

        if len(output) > 0:
            code_response = self.format_code_assistant_message(
                code_response, "\n".join(output)
            )

        self._add_to_conversation(
            role=ConversationRolesInternalEnum.CODE, content=code_response
        )

    def perform_next_step(self) -> Tuple[Message, int]:
        """
        Perform the next step in the conversation.
        Returns the last message in the conversation and number of failed code executions.
        """
        # Generate response
        last_message = self._get_last_message()
        if last_message.role == ConversationRolesInternalEnum.CODE:
            self._send_message_analysis()
        elif last_message.role == ConversationRolesInternalEnum.ANALYSIS:
            self._send_message_code()
        else:
            raise Exception(f"Invalid conversation role: {last_message.role}")

        last_message = self._get_last_message()
        error_limit = 3
        error_count = 0
        while (
            last_message.role == ConversationRolesInternalEnum.CODE
            and "Traceback" in last_message.content
        ):
            # Ask code assistant to fix the error and overwrite previous output. Do until error is fixed.

            error_count += 1
            if error_count >= error_limit:
                raise CodeRetryLimitExceeded(last_message.content)
            self._add_to_conversation(
                role=ConversationRolesInternalEnum.ANALYSIS,
                content="Execution of provided code failed. Please fix the error and try again. \n\nHere is the error message:\n```"
                + last_message.content
                + "```",
            )
            self._send_message_code()
            # Remove artificial message and previous code output
            self._conversation.pop(-2)
            self._conversation.pop(-2)
            last_message = self._get_last_message()

        return self._get_last_message(), error_count

    def get_conversation_json(self) -> str:
        """Get the conversation in json format."""
        return json.dumps([message.model_dump_json() for message in self._conversation])
