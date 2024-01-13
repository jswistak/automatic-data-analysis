import argparse
from os import getenv

from dotenv import load_dotenv
from typing import Union

from core.analysis import analyze
from llm_api.iassistant import IAssistant
from llm_api.openai_assistant import OpenAIAssistant
from prompt_manager.ipromptmanager import IPromptManager
from prompt_manager.few_shot import FewShot
from prompt_manager.zero_shot import ZeroShot
from runtime.iruntime import IRuntime
from runtime.notebook_runtime import NotebookRuntime
from runtime.ssh_python_runtime import SSHPythonRuntime
from llm_api.llama_chat_assistant import LLaMA2ChatAssistant

runtimes: dict[str, IRuntime] = {
    "python-ssh": SSHPythonRuntime,
    "jupyter-notebook": NotebookRuntime,
}

assistants: dict[str, IAssistant] = {
    "openai": OpenAIAssistant,
    "llama-chat": LLaMA2ChatAssistant,
}

prompts: dict[str, IPromptManager] = {
    "few-shot": FewShot,
    "zero-shot": ZeroShot,
}


def get_runtime_kwargs(runtime, code_assistant, analysis_assistant) -> dict:
    """
    Function to get the runtime kwargs based on the runtime and assistants.
    It reads the environment variables and returns the kwargs with the configured values.
    """
    runtime_kwargs = {}
    runtime_kwargs["host"] = getenv("RUNTIME_HOST")
    runtime_kwargs["port"] = getenv("RUNTIME_PORT")
    if runtime == "python-ssh":
        runtime_kwargs["username"] = getenv("USERNAME")
        runtime_kwargs["password"] = getenv("PASSWORD")
    elif runtime == "jupyter-notebook":
        runtime_kwargs["token"] = getenv("TOKEN")
        runtime_kwargs["use_https"] = getenv("RUNTIME_USE_HTTPS") == "true"

    code_assistant_kwargs = {}
    if code_assistant == "openai":
        code_assistant_kwargs["api_key"] = getenv("OPENAI_API_KEY")
    else:
        code_assistant_kwargs["api_key"] = getenv("TOGETHER_API_KEY")

    analysis_assistant_kwargs = {}
    if analysis_assistant == "openai":
        analysis_assistant_kwargs["api_key"] = getenv("OPENAI_API_KEY")
    else:
        analysis_assistant_kwargs["api_key"] = getenv("TOGETHER_API_KEY")

    return {
        "runtime_kwargs": runtime_kwargs,
        "code_assistant_kwargs": code_assistant_kwargs,
        "analysis_assistant_kwargs": analysis_assistant_kwargs,
    }


def main(
    dataset_name: Union[str, None],
    dataset_path: str,
    runtime_name: str,
    code_assistant_name: str,
    analysis_assistant_name: str,
    prompt_name: str,
    analysis_message_limit: Union[int, None] = None,
    **kwargs,
) -> str:
    """
    Program running the automated tabular data analysis using LLM.
    Returns the output of the analysis.
    """
    # print(
    #     f"Running main with args: {dataset_path}, {runtime_name}, {code_assistant_name}, {analysis_assistant_name}, {prompt_name}, {kwargs}"
    # )

    runtime: IRuntime = runtimes.get(runtime_name)(**kwargs.get("runtime_kwargs", {}))
    code_assistant: IAssistant = assistants[code_assistant_name](
        **kwargs.get("code_assistant_kwargs", {})
    )
    analysis_assistant: IAssistant = assistants[analysis_assistant_name](
        **kwargs.get("analysis_assistant_kwargs", {})
    )
    prompt_manager: IPromptManager = prompts[prompt_name](
        **kwargs.get("prompt_kwargs", {})
    )

    if (
        not isinstance(runtime, IRuntime)
        or not isinstance(code_assistant, IAssistant)
        or not isinstance(analysis_assistant, IAssistant)
        or not isinstance(prompt_manager, IPromptManager)
    ):
        raise ValueError(f"Error while initializing the modules.")

    if not dataset_name:
        dataset_name = dataset_path.split("/")[-1]

    runtime.set_report_title(f"Analysis of dataset {dataset_name}")

    return analyze(
        dataset_path,
        runtime,
        code_assistant,
        analysis_assistant,
        prompt_manager,
        analysis_message_limit,
    )


def get_value(env_var: str, args: argparse.Namespace) -> str:
    """
    Set value of variable to the value of the argument if set, otherwise to the value of the environment variable.
    If neither is set, raise an error.
    """

    env_var_name = env_var.upper()

    if getattr(args, env_var):
        return getattr(args, env_var)
    elif getenv(env_var_name):
        return getenv(env_var_name)
    else:
        raise ValueError(f"{env_var} is required but not provided")


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Run the automated tabular data analysis using LLM."
    )
    parser.add_argument(
        "--dataset_path",
        type=str,
        help="Path to the dataset file (CSV)",
        metavar="PATH",
    )
    parser.add_argument(
        "--runtime",
        type=str,
        choices=runtimes.keys(),
        help=f"Runtime type to be used for running the code analysis ({', '.join(runtimes.keys())})",
    )
    parser.add_argument(
        "--code_assistant",
        type=str,
        choices=assistants.keys(),
        help=f"Code assistant type to be used for code completion ({', '.join(assistants.keys())})",
    )
    parser.add_argument(
        "--analysis_assistant",
        type=str,
        choices=assistants.keys(),
        help=f"Analysis assistant type to be used for analysis ({', '.join(assistants.keys())})",
    )
    parser.add_argument(
        "--prompt_type",
        type=str,
        choices=prompts.keys(),
        help=f"Prompt type to be used for generating prompts ({', '.join(prompts.keys())})",
    )
    args = parser.parse_args()

    dataset_path = get_value("dataset_path", args)
    runtime = get_value("runtime", args)
    code_assistant = get_value("code_assistant", args)
    analysis_assistant = get_value("analysis_assistant", args)
    prompt = get_value("prompt_type", args)

    if (
        runtime not in runtimes.keys()
        or code_assistant not in assistants.keys()
        or analysis_assistant not in assistants.keys()
        or prompt not in prompts.keys()
    ):
        raise ValueError(
            f"Environment variables are not set correctly. Please check the documentation."
        )

    kwargs = get_runtime_kwargs(runtime, code_assistant, analysis_assistant)
    main(
        None,
        dataset_path,
        runtime,
        code_assistant,
        analysis_assistant,
        prompt,
        **kwargs,
    )
