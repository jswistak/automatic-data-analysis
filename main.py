from dotenv import load_dotenv
from os import getenv

from conversation import format_code_assistant_message, extract_code_snippets_from_message
from llm_api.iassistant import IAssistant
from llm_api.openai_assistant import OpenAIAssistant
from prompt_manager.few_shot import FewShot
from prompt_manager.ipromptmanager import IPromptManager
# from conversation import Conversation
from runtime.iruntime import IRuntime
from utils import (
    Colors,
    print_assistant_message,
    print_user_message,
    print_message_prefix,
)
from runtime.ssh_python_runtime import SSHPythonRuntime
from runtime.notebook_runtime import NotebookRuntime
from datetime import datetime
from models.models import ConversationRolesInternalEnum, Message, LLMType
import argparse
import json

# TODO: Rewrite the cell in case of error

def analyze(dataset_path: str, runtime: IRuntime, code_assistant: IAssistant, analysis_assistant: IAssistant,
            prompt: IPromptManager):
    # region: Loading dataset into runtime environment
    conv: list[Message] = []
    dataset_file_name = dataset_path.split("/")[-1]
    runtime.upload_file(getenv("DATASET_PATH"), dataset_file_name)

    load_dataset_code = "\n".join(
        ["import pandas as pd", f"df= pd.read_csv('{dataset_file_name}', sep=',')"]
    )
    cell_idx = runtime.add_code(load_dataset_code)
    runtime.execute_cell(cell_idx)

    cell_idx = runtime.add_code("df.head()")
    runtime.execute_cell(cell_idx)
    initial_message = "Dataset is loaded into the runtime in the variable 'df'.'\nYou can try to print the first 5 rows of the dataset by executing the following code: ```python\ndf.head()```"
    conv.append(Message(role=ConversationRolesInternalEnum.CODE, content=format_code_assistant_message(initial_message,
                                                                                                       runtime.get_cell_output_stream(
                                                                                                           cell_idx))))

    print_user_message(conv[-1].content)
    while "q" not in input(
            f"{Colors.BOLD_BLACK}Press 'q' to quit or any other key to continue: {Colors.END}"
    ):
        # Generate response
        analysis_conv = prompt.generate_conversation_context(conv, ConversationRolesInternalEnum.ANALYSIS, LLMType.GPT4)
        analysis_assistant_message = analysis_assistant.generate_response(analysis_conv)

        print(f"{Colors.BOLD_BLACK}Assistant: {Colors.END}", end="")
        print_user_message(analysis_assistant_message)
        conv.append(Message(role=ConversationRolesInternalEnum.ANALYSIS, content=analysis_assistant_message))
        if "q" in input(f"{Colors.BOLD_BLACK}Press 'q' to quit or any other key to continue: {Colors.END}"):
            break

        # Generate response
        code_conv = prompt.generate_conversation_context(conv, ConversationRolesInternalEnum.CODE, LLMType.GPT4)
        code_assistant_message = code_assistant.generate_response(code_conv)

        print(f"{Colors.BOLD_BLACK}Assistant: {Colors.END}", end="")
        try:
            code_snippets = extract_code_snippets_from_message(code_assistant_message)
            code_outputs = []
            for snippet in code_snippets:
                if code.startswith("python"):
                    code = code[6:]
                    cell_idx = runtime.add_code(code)
                    runtime.execute_cell(cell_idx)
                    retval = runtime.get_cell_output_stream(cell_idx)
                    plot_in_output = runtime.check_if_plot_in_output(cell_idx)
                    code_outputs.append(retval)
            msg = Message(role=ConversationRolesInternalEnum.CODE, content=format_code_assistant_message(code_assistant_message, "\n\n".join(code_outputs)))
        except:
            msg = Message(role=ConversationRolesInternalEnum.CODE, content=code_assistant_message)



        print_user_message(msg.content)
        conv.append(msg)


    report_path = runtime.generate_report(
        "reports", datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    )
    print(f"Report has been saved to {report_path}")

    json_models = [model.model_dump_json() for model in conv]

    with open("conversation.json", "w") as f:
        json.dump(json_models, f, indent=4)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-dataset", type=str)
    parser.add_argument(
        "-runtime",
        type=str,
        default="jupyter-notebook",
        choices=["python-ssh", "jupyter-notebook", "apache-zeppelin"],
    )
    load_dotenv()
    args = parser.parse_args()  # Arguments have precedence over environment variables

    if args.dataset:
        dataset_path = args.dataset
    else:
        dataset_path = getenv("DATASET_PATH")
    if not dataset_path:
        raise ValueError("Dataset path is required but not provided")

    if args.runtime:
        runtime_type = args.runtime
    else:
        runtime_type = getenv("RUNTIME_TYPE")
    if not runtime_type:
        raise ValueError("Runtime type is required but not provided")

    match runtime_type:
        case "python-ssh":
            runtime = SSHPythonRuntime(
                host=getenv("SSH_HOST"),
                port=getenv("SSH_PORT"),
                username=getenv("SSH_USERNAME"),
                password=getenv("SSH_PASSWORD"),
            )
        case "jupyter-notebook":
            runtime = NotebookRuntime(
                host=getenv("JUPYTER_HOST"),
                port=getenv("JUPYTER_PORT"),
                token=getenv("JUPYTER_TOKEN"),
            )
        case "apache-zeppelin":
            raise NotImplementedError("Apache Zeppelin is not supported yet")
        case _:
            raise ValueError(f"Runtime type {runtime_type} is not supported")

    # WIP
    load_dotenv()
    code_assistant = OpenAIAssistant(getenv("OPENAI_API_KEY"))
    analysis_assistant = OpenAIAssistant(getenv("OPENAI_API_KEY"))
    prompt = FewShot()
    analyze(dataset_path, runtime, code_assistant, analysis_assistant, prompt)
