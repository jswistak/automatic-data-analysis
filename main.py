from dotenv import load_dotenv
from os import getenv
from conversation import Conversation
from completion import ConversationRoles
from utils import Colors, print_assistant_message, print_user_message
from runtime.ssh_python_runtime import SSHPythonRuntime
from prompts import INITIAL_PROMPT, PROMPT_SUFFIX
from datetime import datetime


def main():
    load_dotenv()
    runtime = SSHPythonRuntime(
        host=getenv("SSH_HOST"),
        username=getenv("SSH_USERNAME"),
        password=getenv("SSH_PASSWORD"),
        port=getenv("SSH_PORT"),
    )

    # region: Loading dataset into runtime environment
    dataset_file_name = getenv("DATASET_PATH").split("/")[-1]
    runtime.upload_file(getenv("DATASET_PATH"), dataset_file_name)

    load_dataset_code = "\n".join(
        ["import pandas as pd", f"df= pd.read_csv('{dataset_file_name}', sep=',')"]
    )
    cell_idx = runtime.add_code(load_dataset_code)
    runtime.execute_cell(cell_idx)
    # endregion

    # Setting initial conversation goals
    bot: Conversation = Conversation(
        conversation=[
            {
                "role": ConversationRoles.SYSTEM,
                "content": INITIAL_PROMPT,
            },
        ],
        python_code_executed=load_dataset_code,
    )

    cell_idx = runtime.add_code("df.head()")
    runtime.execute_cell(cell_idx)
    user_message: str = (
        "Here is a dataset I want you to analyze. "
        "It is a CSV file, loaded into pandas as a 'df' variable. Here is the output of the ```python\df.head()```\n"
        f"{runtime.get_cell_output(cell_idx)}"
    )

    while "q" not in input(
        f"{Colors.BOLD_BLACK}Press 'q' to quit or any other key to continue: {Colors.END}"
    ):
        # Generate response
        print_user_message(user_message)
        assistant_message, code_snippets = bot.generate_response_with_snippets(
            ConversationRoles.USER, user_message, system_message_suffix=PROMPT_SUFFIX
        )
        # r = get_response(conversation)
        # assistant_message = extract_message_from_response(r)
        # conversation.append({"role": "assistant", "content": assistant_message})
        print_assistant_message(assistant_message, code_snippets)

        """ 
        Since the code will be executed in the virtual environment,
        we will NOT ask for a confirmation to execute the code.
        """
        # if len(code_snippets) > 0:
        #     user_input: str = input(
        #         f"{Colors.BOLD_BLACK}Do you want to execute code? (y/n): {Colors.END}"
        #     )
        #     if user_input.lower()[0] != "y":
        #         break

        # Execute code
        if len(code_snippets) == 0:
            user_message = "I have not found any code snippets. Please provide me with python code to execute."
            continue

        user_message: str = (
            f"I have found {len(code_snippets)} code snippets. Here is the output of:"
        )

        for code in code_snippets:
            retval = None
            if code.startswith("python"):
                code = code[6:]
                bot.add_executed_code(code)
                cell_idx = runtime.add_code(code)
                runtime.execute_cell(cell_idx)
                retval = runtime.get_cell_output(cell_idx)
            user_message = (
                user_message
                + "\n"
                + code
                + "\n"
                + (
                    retval
                    if retval
                    else (
                        "Code has been executed! Unfortunately, there is no output for this code snippet. Please remember to print the output."
                        if ".show" not in code
                        else "While showing the plots it very helpful for me to understand the data. "
                        "Please also remember that I'm unable to provide you with the plots. Can you then also print the required numerical description for me to present it to you?"
                    )
                )
            )

        # TODO: summarize conversation
        # Summarize the conversation from time to time to keep it short
        # if len(conversation) > 4:
        #     bot.summarize_conversation(conversation)

    # Save conversation
    bot.save_conversation_to_file()
    report_path = runtime.generate_report("reports", datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    print(f"Report has been saved to {report_path}")


if __name__ == "__main__":
    main()
