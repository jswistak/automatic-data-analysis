import pandas as pd
from typing import List


class Colors:
    """Color codes for terminal output."""

    # Regular Colors
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


def print_user_message(user_message: str) -> None:
    """Colorful formatting of user message."""
    print(
        f"{Colors.BOLD_GREEN}User message:{Colors.END}",
        f"{Colors.GREEN}\n",
        user_message,
        f"{Colors.END}\n",
    )


def print_assistant_message(assistant_message: str, code_snippets: List[str]) -> None:
    """Colorful formatting of assistant message and code snippets."""
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

def print_message_suffx(message_suffix: str) -> None:
    """Colorful formatting of message suffix."""
    print(
        f"{Colors.BOLD_YELLOW}Message suffix:{Colors.END}",
        f"{Colors.YELLOW}\n",
        message_suffix,
        f"{Colors.END}\n",
    )