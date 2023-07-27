import contextlib
from conversation import Conversation, ConversationRoles
from utils import Colors, load_csv_data, print_assistant_message, print_user_message
from exec import CodeExecutor


def main():
    dataset_file_path = "data.csv"
    df = load_csv_data(dataset_file_path)

    code_sandbox = CodeExecutor(env={"df": df})

    python_code_executed: str = (
        """pd.read_csv("data.csv", sep=",")\nprint(df.head())\n"""
    )

    # Setting initial conversation goals
    bot: Conversation = Conversation(
        conversation=[
            {
                "role": "system",
                "content": "In this interaction, the AI assistant will proactively take actions by generating a code to be run on "
                "a CSV dataset loaded into pandas and available under variable 'df', perform data cleaning using Python programming language, "
                "conduct exploratory data analysis (EDA), and make inferences based "
                "on the analysis. The AI assistant will guide the user through the data processing by providing code snippets "
                "and analysis steps, providing insights without explicit prompting.",
            },
        ],
        python_code_executed=python_code_executed,
    )

    user_message: str = (
        "Here is a dataset I want you to analyze. "
        "It is a CSV file, loaded into pandas as a 'df' variable. Here is the output of the ```python\df.head()```\n"
        f"{df.head()}"
    )

    while "q" not in input(
        f"{Colors.BOLD_BLACK}Press 'q' to quit or any other key to continue: {Colors.END}"
    ):
        # Generate response
        print_user_message(user_message)
        assistant_message, code_snippets = bot.generate_response_with_snippets(
            ConversationRoles.USER, user_message
        )
        # r = get_response(conversation)
        # assistant_message = extract_message_from_response(r)
        # conversation.append({"role": "assistant", "content": assistant_message})
        print_assistant_message(assistant_message, code_snippets)

        if len(code_snippets) > 0:
            user_input: str = input(
                f"{Colors.BOLD_BLACK}Do you want to execute code? (y/n): {Colors.END}"
            )
            if user_input.lower()[0] != "y":
                break

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
                try:
                    bot.add_executed_code(code)
                    retval = code_sandbox.execute_code(code)
                except Exception as e:
                    retval = f"Error occurred while executing code: {e}"
            user_message = (
                user_message
                + "\n"
                + code
                + "\n"
                + (
                    retval
                    if retval
                    else (
                        "Code has been executed without any errors! Unfortunately, there is no output for this code snippet. Please remember to print the output."
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


if __name__ == "__main__":
    main()
