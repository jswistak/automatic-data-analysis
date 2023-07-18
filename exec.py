from io import StringIO
from contextlib import redirect_stdout

class CodeExecutor:
    # TODO: create real sandbox environment
    # TODO: support jupyter notebooks
    def __init__(self, env: dict = None):
        for k, v in env.items():
            setattr(self, k, v)

    def execute_code(self, code: str) -> str:
        for k, v in self.__dict__.items():
            exec(f"{k} = self.{k}")

        stdout_redirection = StringIO()
        with redirect_stdout(stdout_redirection):
            exec(code)

        return stdout_redirection.getvalue()

