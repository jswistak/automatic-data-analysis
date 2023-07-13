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

df = pd.read_csv("data.csv", sep=",")
print(df.head())
conversation = [
    {
        "role": "system",
        "content": "\
          In this interaction, the AI assistant will proactively take actions by generateing a code to be run on \
          a CSV dataset loaded into pandas and available under variable 'df', perform data cleaning using Python programming language, \
          create a new dataset, conduct exploratory data analysis (EDA), and make inferences based \
          on the analysis. The AI assistant will guide the user through the data processing \
          and analysis steps, providing insights without explicit prompting.",
    },
    {
        "role": "user",
        "content": f"Hello, here is a dataset I want you to analyze. \
          It is a CSV file, loaded into pandas as a 'df' variable. Here is the output of the ```python\df.head()```\n\
          {df.head()}",
    },
]

# r = get_response(conversation)
# print(extract_message_from_response(r))

while "q" not in input("Press 'q' to quit or any other key to continue: "):
    r = get_response(conversation)
    assistant_message = extract_message_from_response(r)
    conversation.append({"role": "assistant", "content": assistant_message})
    print(assistant_message)
    print("### Code Snippets ###")
    code_snippets = extract_code_snippets_from_response(r)
    print(code_snippets)
    print("### End of Code Snippets ###")
    user_input = input("Do you want to execute code? (y/n): ")
    if user_input.lower() not in ["y", "yes"]:
        break

    # Execute code

    user_message = (
        f"I have found {len(code_snippets)} code snippets. Here is the output of:\n"
    )
    if len(code_snippets) == 0:
        user_message = "I have not found any code snippets. Please provide me with python code to execute."
    output = StringIO()
    with contextlib.redirect_stdout(output):
        # print("Trying to execute code...")
        for code in code_snippets:
            # print("### Executing code ###")
            # print()
            if code.startswith("python"):
                code = code[6:]
                try:
                    exec(code)
                except Exception as e:
                    print(f"Error occurred while executing code: {e}")
            # exec(code)
            user_message = (
                user_message
                + "\n"
                + code
                + "\n"
                + (
                    output.getvalue()
                    if output.getvalue()
                    else "Unfortunately, there is no output."
                )
            )
            output.truncate(0)

    conversation.append({"role": "user", "content": user_message})

    print()
    print(conversation)
    # r = get_response(conversation)
    # print(extract_message_from_response(r))
    # print(extract_code_snippets_from_response(r))
    # conversation.append({"role": "system", "content": extract_message_from_response(r)})

# r = get_response(conversation)

# print(extract_message_from_response(r))
# print(extract_code_snippets_from_response(r))
