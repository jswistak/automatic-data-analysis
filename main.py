import json
import openai
import os
import contextlib
import pandas as pd
from dotenv import load_dotenv
from io import StringIO
from completion import (
    get_response,
    extract_code_snippets_from_response,
    extract_message_from_response,
)
from conversation import save_conversation_to_file
from utils import Colors


def main():
    df = pd.read_csv("data.csv", sep=",")
    python_code_executed = """pd.read_csv("data.csv", sep=",")\n"""

    print(df.head())
    conversation = [
        {
            "role": "system",
            "content": "In this interaction, the AI assistant will proactively take actions by generateing a code to be run on "
            "a CSV dataset loaded into pandas and available under variable 'df', perform data cleaning using Python programming language, "
            "conduct exploratory data analysis (EDA), and make inferences based "
            "on the analysis. The AI assistant will guide the user through the data processing by providing code snippets "
            "and analysis steps, providing insights without explicit prompting.",
        },
        {
            "role": "user",
            "content": "Here is a dataset I want you to analyze"
            "It is a CSV file, loaded into pandas as a 'df' variable. Here is the output of the ```python\df.head()```\n"
            f"{df.head()}",
        },
    ]

    while "q" not in input("Press 'q' to quit or any other key to continue: "):
        r = get_response(conversation)
        assistant_message = extract_message_from_response(r)
        conversation.append({"role": "assistant", "content": assistant_message})
        print(
            f"{Colors.BOLD_BLUE}Assistant message:{Colors.END}\n",
            f"{Colors.CYAN}",
            assistant_message,
            f"{Colors.END}",
        )
        # print("### Code Snippets ###")
        code_snippets = extract_code_snippets_from_response(r)
        print(code_snippets)
        # print("### End of Code Snippets ###")
        if len(code_snippets) > 0:
            user_input = input("Do you want to execute code? (y/n): ")
            if user_input.lower() not in ["y", "yes"]:
                break

        # Execute code

        user_message = (
            f"I have found {len(code_snippets)} code snippets. Here is the output of:"
        )
        if len(code_snippets) == 0:
            user_message = "I have not found any code snippets. Please provide me with python code to execute."
        output = StringIO()
        with contextlib.redirect_stdout(output):
            for code in code_snippets:
                if code.startswith("python"):
                    code = code[6:]
                    try:
                        # TODO: run it in a sandbox environment
                        python_code_executed += code + "\n"
                        exec(code)
                    except Exception as e:
                        print(f"Error occurred while executing code: {e}")
                user_message = (
                    user_message
                    + "\n"
                    + code
                    + "\n"
                    + (
                        output.getvalue()
                        if output.getvalue()
                        else (
                            "Code has been executed without any errors! Unfortunately, there is no output for this code snippet. Please remember to print the output."
                            if ".show" not in code
                            else "While showing the plots it very helpful for me to understand the data. "
                            "Please also remember that I'm unable to provide you with the plots. Can you then also print the required numerical description for me to present it to you?"
                        )
                    )
                )
                output.truncate(0)

        print(
            f"{Colors.BOLD_GREEN}User message:{Colors.END}\n",
            f"{Colors.BOLD_CYAN}",
            user_message,
            f"{Colors.END}",
        )
        conversation.append({"role": "user", "content": user_message})

        # Summarize the conversation from time to time to keep it short

    # Save conversation
    print("Python code executed:\n", python_code_executed)
    save_conversation_to_file(conversation, python_code_executed=python_code_executed)


if __name__ == "__main__":
    main()
