from dotenv import load_dotenv
from os import getenv

from llm_api.openai_assistant import OpenAIAssistant
from prompt_manager.few_shot import FewShot


from runtime.ssh_python_runtime import SSHPythonRuntime
from runtime.notebook_runtime import NotebookRuntime
import argparse

from core.analysis import analyze


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
