import os
from main import main, get_runtime_kwargs
from dotenv import load_dotenv
from core.analysis import CodeRetryLimitExceeded

load_dotenv()
together_token = os.getenv("TOGETHER_API_KEY")
openai_token = os.getenv("OPENAI_API_KEY")

prompting_techniques = ["zero-shot", "few-shot"]
assistants = [
    "llama-chat",
    "openai",
    "mixtral-8x7b",
]

analysis_message_limit = 8
runtime = "jupyter-notebook"
report_params_no = {
    "zero-shot_llama-chat": 1,
    "zero-shot_openai": 2,
    "zero-shot_mixtral-8x7b": 3,
    "few-shot_llama-chat": 4,
    "few-shot_openai": 5,
    "few-shot_mixtral-8x7b": 6,
}

dataset_path = "data/castles.csv"
dataset_name = dataset_path.split("/")[-1].split(".")[0]


for assistant in assistants:
    for prompting_technique in prompting_techniques:
        kwargs = get_runtime_kwargs(
            runtime,
            prompting_technique,
            assistant,
        )
        kwargs["analysis_assistant_kwargs"]["api_key"] = (
            openai_token if assistant == "openai" else together_token
        )
        kwargs["code_assistant_kwargs"]["api_key"] = (
            openai_token if assistant == "openai" else together_token
        )
        report_no = report_params_no[f"{prompting_technique}_{assistant}"]
        try:
            output_pdf_path, error_count, code_messages_missing_snippets = main(
                dataset_name,
                dataset_path,
                runtime,
                assistant,
                assistant,
                prompting_technique,
                analysis_message_limit=analysis_message_limit,
                output_pdf_path=f"../{dataset_name}_{report_no}.pdf",
                **kwargs,
            )
        except CodeRetryLimitExceeded as e:
            print(e)
            continue
        print(output_pdf_path)
        print("Error Count:", error_count)
        print("Code Messages Missing Snippets:", code_messages_missing_snippets)
        # create text file with error count and code messages missing snippets
        with open(f"data/{dataset_name}_{report_no}.txt", "w") as f:
            f.write(f"Error Count: {error_count}\n")
            f.write(
                f"Code Messages Missing Snippets: {code_messages_missing_snippets}\n"
            )
