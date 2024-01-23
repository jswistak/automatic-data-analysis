import json
import csv
from datetime import datetime
from typing import Union

from core.conversation import Conversation
from core.utils import Colors, print_message
from llm_api.iassistant import IAssistant
from models.models import ConversationRolesInternalEnum, Message
from prompt_manager.ipromptmanager import IPromptManager
from runtime.iruntime import IRuntime

# TODO: Rewrite the cell in case of error


class CodeRetryLimitExceeded(Exception):
    """Exception raised when too many errors occur during code execution."""

    def __init__(self, message="Exceeded code retry limit"):
        self.message = message
        super().__init__(self.message)


def save_to_csv(data):
    filename = "results.csv"
    # Check if file exists
    file_exists = False
    try:
        with open(filename, "r") as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    # Open the file in append mode ('a'). If the file doesn't exist, it will be created.
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        if not file_exists:
            # If file does not exist, write the header
            writer.writerow(
                [
                    "code_assistant_type",
                    "prompt_type",
                    "dataset_name",
                    "report_path",
                    "error_count",
                    "code_messages_missing_snippets",
                    "msg_count",
                    "analysis_message_limit",
                    "exception",
                ]
            )
            # Rest can be calculated from these formulas:
            # analyst_count = (msg_count + 1) // 2
            # code_count = msg_count // 2 + error_count
            # total_assistant_requests = msg_count + error_count

        writer.writerow(data)


def analyze(
    dataset_path: str,
    runtime: IRuntime,
    code_assistant: IAssistant,
    analysis_assistant: IAssistant,
    prompt: IPromptManager,
    analysis_message_limit: Union[int, None] = None,
    output_pdf_path: str = None,
) -> tuple[str, int, int]:
    """
    Conduct the automated tabular data analysis using LLM for a given dataset.
    Returns the path to the generated report.
    """
    conv_list: list[Message] = []
    dataset_file_name = dataset_path.split("/")[-1]
    runtime.upload_file(dataset_path, dataset_file_name)
    try:
        report_name = output_pdf_path.split("/")[-1].split(".")[0]
    except:
        report_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if report_name == "":
        report_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    load_dataset_code = "\n".join(
        ["import pandas as pd", f"df= pd.read_csv('{dataset_file_name}', sep=',')"]
    )
    cell_idx = runtime.add_code(load_dataset_code)
    runtime.execute_cell(cell_idx)

    initial_message = "Dataset is loaded into the runtime in the variable 'df'.'\nYou can try to print the first 5 rows of the dataset by executing the following code: ```python\ndf.head()```"
    runtime.add_description(initial_message)

    cell_idx = runtime.add_code("df.head()")

    runtime.execute_cell(cell_idx)
    conv_list.append(
        Message(
            role=ConversationRolesInternalEnum.CODE,
            content=Conversation.format_code_assistant_message(
                initial_message, runtime.get_cell_output_stream(cell_idx)
            ),
        )
    )
    print_message(conv_list[-1], Colors.PURPLE)

    conv = Conversation(runtime, code_assistant, analysis_assistant, prompt, conv_list)
    error_count = 0
    msg_count = 0
    try:
        while analysis_message_limit is None or msg_count < analysis_message_limit:
            if analysis_message_limit is None and "q" in input(
                f"{Colors.BOLD_BLACK.value}Press 'q' to quit or any other key to continue: {Colors.END.value}"
            ):
                break

            msg = conv.perform_next_step()
            msg_count += 1
            code_retry_limit = 3
            while conv.last_msg_contains_execution_errors():
                error_count += 1
                print_message(msg, Colors.RED)
                if code_retry_limit == 0:
                    print("Exceeded code retry limit")
                    raise CodeRetryLimitExceeded(
                        f"Code assistant exceeded retry limit for code execution and could not fix the code for 3 consecutive times."
                    )
                msg = conv.fix_last_code_message()
                code_retry_limit -= 1

            print_message(
                msg,
                Colors.PURPLE
                if msg.role == ConversationRolesInternalEnum.CODE
                else Colors.BLUE,
            )
    except Exception as e:
        try:
            report_path = runtime.generate_report("reports", report_name)
        except Exception as ex:
            report_path = None
        save_to_csv(
            [
                code_assistant.__class__.__name__,
                prompt.__class__.__name__,
                dataset_file_name,
                report_path,
                error_count,
                conv.code_messages_missing_snippets,
                msg_count,
                analysis_message_limit,
                e,
            ]
        )

        raise e

    report_path = runtime.generate_report("reports", report_name)

    print(
        f"{Colors.BOLD_RED.value}Total number of errors: {error_count}{Colors.END.value}"
    )
    print(
        f"{Colors.BOLD_YELLOW.value}Report has been saved to {report_path}{Colors.END.value}"
    )
    print(
        f"{Colors.BOLD_BLUE.value}Code Assistant messages missing code snippets: {conv.code_messages_missing_snippets}{Colors.END.value}"
    )
    save_to_csv(
        [
            code_assistant.__class__.__name__,
            prompt.__class__.__name__,
            dataset_file_name,
            report_path,
            error_count,
            conv.code_messages_missing_snippets,
            msg_count,
            analysis_message_limit,
            None,
        ]
    )

    conv_json = conv.get_conversation_json()
    conv_path = f"conversations/conversation-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    with open(conv_path, "w") as f:
        json.dump(conv_json, f, indent=4)
    print(
        f"{Colors.BOLD_YELLOW.value}Conversation has been saved to {conv_path}{Colors.END.value}"
    )
    return report_path, error_count, conv.code_messages_missing_snippets
