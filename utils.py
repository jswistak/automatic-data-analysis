import pandas as pd


class Colors:
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"

    # Bold Colors
    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_PURPLE = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"

    # Reset Color
    END = "\033[0m"


def load_csv_data(data_path: str) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv(data_path, sep=",")
    print(
        f"{Colors.BOLD_YELLOW}Dataset '{data_path}' loaded into pandas. Head:{Colors.END}",
        f"{Colors.YELLOW}\n",
        df.head(),
        f"{Colors.END}\n",
    )
    return df


def print_user_message(user_message: str) -> None:
    print(
        f"{Colors.BOLD_GREEN}User message:{Colors.END}",
        f"{Colors.GREEN}\n",
        user_message,
        f"{Colors.END}\n",
    )


def print_assistant_message(assistant_message: str, code_snippets) -> None:
    print(
        f"{Colors.BOLD_BLUE}Assistant message:{Colors.END}",
        f"{Colors.CYAN}\n",
        assistant_message,
        f"{Colors.END}\n",
    )
    code_snippets = "\n\n".join(code_snippets)
    print(
        f"{Colors.BOLD_RED}Assistant message code snippets:{Colors.END}",
        f"{Colors.RED}\n",
        code_snippets if code_snippets else "No code snippets",
        f"{Colors.END}\n",
    )
