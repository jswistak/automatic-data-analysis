import paramiko
from typing import Union
from runtime.iruntime import IRuntime


class _SSHPythonRuntimeCell:
    __slots__ = ["content", "type", "output"]

    def __init__(self, content: str, type: str):
        self.content = content
        self.type = type
        self.output = None


class SSHPythonRuntime(IRuntime):
    """
    Remote python runtime, handled as an interactive python shell via SSH.

    Report is generated as a markdown file with the code snippets and their outputs.
    """

    def __init__(
        self, username: str, password: str, host: str = "127.0.0.1", port: int = 22
    ):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=host, username=username, password=password, port=port)

        self.shell = self.ssh.invoke_shell()
        self._execute_command("python")

        self.cells: list[_SSHPythonRuntimeCell] = []

    def __del__(self):
        self.shell.close()
        self.ssh.close()

    def add_description(self, description: str) -> int:
        self.cells.append(_SSHPythonRuntimeCell(description, "description"))
        return len(self.cells) - 1

    def add_code(self, code: str) -> int:
        self.cells.append(_SSHPythonRuntimeCell(code, "code"))
        return len(self.cells) - 1

    def remove_cell(self, cell_index: int) -> None:
        del self.cells[cell_index]

    def execute_cell(self, cell_index: int) -> None:
        cell = self.cells[cell_index]
        if cell.type != "code":
            return

        commands = cell.content.split("\n")
        output = ""
        for c in commands:
            retval = self._execute_command(c).strip()
            if retval != "":
                output += retval + "\n"

        self.cells[cell_index].output = output.strip()

    def get_cell_output(self, cell_index: int) -> Union[str, None]:
        cell = self.cells[cell_index]
        if cell.type != "code":
            return None

        return cell.output

    def upload_file(self, local_path: str, dest_file_path: str) -> None:
        sftp_client = self.ssh.open_sftp()
        sftp_client.put(local_path, dest_file_path)
        sftp_client.close()

    def generate_report(self, dest_dir: str, filename: str) -> str:
        markdown = ""

        for i, cell in enumerate(self.cells):
            if cell.type == "description":
                markdown += cell.content + "\n\n"
            else:
                markdown += f"```python\n{cell.content}\n```\n"
                if cell.output is not None:
                    markdown += f"```python\n# Output:\n{cell.output}\n```\n"

        markdown_path = f"{dest_dir}/{filename}.md"

        with open(markdown_path, "w") as f:
            f.write(markdown)

        return markdown_path

    def _execute_command(self, command: str) -> str:
        """
        Execute the given command in the remote shell.

        Returns:
            All output streams (both stdout and stderr) of the command.
        """
        # TODO: handle plotting

        command = command.strip("\n")
        self.shell.send(command + "\n")

        output_raw = ""
        self.shell.recv(len(command) + 1)
        while not output_raw.endswith(">>> "):
            output_raw += self.shell.recv(1024).decode("utf-8")

        return output_raw.replace(">>> ", "")
