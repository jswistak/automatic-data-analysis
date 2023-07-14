import json


def save_conversation_to_file(conversation: list, python_code_executed: str) -> None:
    print("Saving conversation...")
    # Retrieve the latest conversation number
    number_file_path = "latest_conversation_number.txt"
    try:
        with open(number_file_path, "r") as number_file:
            latest_conversation_number = int(number_file.read())
    except FileNotFoundError:
        latest_conversation_number = 1

    conversation_path = (
        f"conversations/conversation{latest_conversation_number:04d}.json"
    )
    with open(conversation_path, "w") as f:
        json.dump(conversation, f)

    if python_code_executed is not None:
        code_path = f"conversations/conversation{latest_conversation_number:04d}.py"
        with open(code_path, "w") as f:
            f.write(python_code_executed)

    latest_conversation_number += 1
    with open(number_file_path, "w") as number_file:
        number_file.write(str(latest_conversation_number))

    print("Conversation saved to", conversation_path)
