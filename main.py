from dotenv import load_dotenv
from os import getenv

from llm_api.openai_assistant import OpenAIAssistant
from prompt_manager.few_shot import FewShot, ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT


from runtime.ssh_python_runtime import SSHPythonRuntime
from runtime.notebook_runtime import NotebookRuntime
import argparse

from core.analysis import analyze

runtimes = {
    "python-ssh": SSHPythonRuntime,
    "jupyter-notebook": NotebookRuntime,
}

assistants = {
    "openai": OpenAIAssistant,
}

prompts = {
    "few-shot": FewShot,
}


def main(
    dataset_path: str,
    runtime: str,
    code_assistant: str,
    analysis_assistant: str,
    prompt: str,
    **kwargs,
):
    runtime = runtimes[runtime](**kwargs.get("runtime_kwargs", {}))
    code_assistant = assistants[code_assistant](
        **kwargs.get("code_assistant_kwargs", {})
    )
    analysis_assistant = assistants[analysis_assistant](
        **kwargs.get("analysis_assistant_kwargs", {})
    )
    prompt = prompts[prompt](**kwargs.get("prompt_kwargs", {}))
    analyze(dataset_path, runtime, code_assistant, analysis_assistant, prompt)


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
        "--prompt",
        type=str,
        choices=prompts.keys(),
        help=f"Prompt type to be used for generating prompts ({', '.join(prompts.keys())})",
    )
    args = parser.parse_args()

    dataset_path = get_value("dataset_path", args)
    runtime = get_value("runtime", args)
    code_assistant = get_value("code_assistant", args)
    analysis_assistant = get_value("analysis_assistant", args)
    prompt = get_value("prompt", args)

    if (
        runtime not in runtimes.keys()
        or code_assistant not in assistants.keys()
        or analysis_assistant not in assistants.keys()
        or prompt not in prompts.keys()
    ):
        raise ValueError(
            f"Invalid argument provided. Please check the available options for each argument."
        )

    runtime_kwargs = {}
    runtime_kwargs["host"] = getenv("HOST")
    runtime_kwargs["port"] = getenv("PORT")
    if runtime == "python-ssh":
        runtime_kwargs["username"] = getenv("USERNAME")
        runtime_kwargs["password"] = getenv("PASSWORD")
    elif runtime == "jupyter-notebook":
        runtime_kwargs["token"] = getenv("TOKEN")

    code_assistant_kwargs = {}
    if code_assistant == "openai":
        code_assistant_kwargs["api_key"] = getenv("OPENAI_API_KEY")

    analysis_assistant_kwargs = {}
    if analysis_assistant == "openai":
        analysis_assistant_kwargs["api_key"] = getenv("OPENAI_API_KEY")

    kwargs = {
        "runtime_kwargs": runtime_kwargs,
        "code_assistant_kwargs": code_assistant_kwargs,
        "analysis_assistant_kwargs": analysis_assistant_kwargs,
    }
    main(dataset_path, runtime, code_assistant, analysis_assistant, prompt, **kwargs)
