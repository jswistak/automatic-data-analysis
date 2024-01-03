from enum import Enum

from models.models import Message


class Colors(str, Enum):
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


def print_message(msg: Message, color: Colors) -> None:
    """Colorful formatting of user message."""
    print(
        f"{Colors.BOLD_GREEN.value}{msg.role}{Colors.END.value}",
        f"{color.value}\n",
        msg.content,
        f"{Colors.END.value}\n",
    )
