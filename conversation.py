import json
from typing import List

from models.models import Message, ConversationRolesInternalEnum, LLMType
from runtime.iruntime import IRuntime
from llm_api.iassistant import IAssistant
from prompt_manager.ipromptmanager import IPromptManager
from utils import print_message, Colors


class Conversation:
    """Conversation class that handles the conversation flow and stores the conversation history."""
    def __init__(self, runtime: IRuntime, code_assistant: IAssistant, analysis_assistant: IAssistant,
                 prompt: IPromptManager, conversation: List[Message] = None):
        self.conversation: List[Message] = conversation
        self.runtime: IRuntime = runtime
        self.code_assistant: IAssistant = code_assistant
        self.analysis_assistant: IAssistant = analysis_assistant
        self.prompt: IPromptManager = prompt

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
        return self.conversation

    def _add_to_conversation(self, role: ConversationRolesInternalEnum, content: str) -> None:
        self.conversation.append(Message(role=role, content=content))

    def _get_last_message(self) -> Message:
        return self.conversation[-1]

    def _send_message_analysis(self) -> None:
        analysis_conv = self.prompt.generate_conversation_context(self.conversation,
                                                                  ConversationRolesInternalEnum.ANALYSIS, LLMType.GPT4)
        analysis_response = self.analysis_assistant.generate_response(analysis_conv)
        self._add_to_conversation(ConversationRolesInternalEnum.ANALYSIS, analysis_response)
        print_message(self._get_last_message(), Colors.BLUE)

    def _execute_python_snippet(self, code: str) -> int:
        cell_idx = self.runtime.add_code(code)
        self.runtime.execute_cell(cell_idx)
        return cell_idx

    def _check_if_plot_in_output(self, cell_idx: int) -> bool:
        return self.runtime.check_if_plot_in_output(cell_idx)

    def _get_cell_output_stream(self, cell_idx: int) -> str:
        return self.runtime.get_cell_output_stream(cell_idx)

    def _send_message_code(self) -> None:
        code_conv = self.prompt.generate_conversation_context(self.conversation, ConversationRolesInternalEnum.CODE,
                                                              LLMType.GPT4)
        code_response = self.code_assistant.generate_response(code_conv)
        code_snippets = self._extract_code_snippets_from_message(code_response)
        output = []
        for code_snippet in code_snippets:
            if code_snippet.startswith("python"):
                code = code_snippet[6:]
                cell_idx = self._execute_python_snippet(code)
                output.append(self._get_cell_output_stream(cell_idx))
                if self._check_if_plot_in_output(cell_idx):
                    output[-1] = "Plot generated, but cannot be interpreted in a text format."
        if len(output) > 0:
            code_response = self.format_code_assistant_message(code_response, "\n".join(output))

        self._add_to_conversation(role=ConversationRolesInternalEnum.CODE, content=code_response)
        print_message(self._get_last_message(), Colors.PURPLE)

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

    def get_conversation_json(self) -> str:
        """Get the conversation in json format."""
        return json.dumps([message.model_dump_json() for message in self.conversation])
