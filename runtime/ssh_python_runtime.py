import paramiko
from typing import Union, Tuple, List
import re
import uuid
from runtime.iruntime import IRuntime


class _SSHPythonRuntimeCell:
    __slots__ = ["content", "type", "output", "plots"]

    def __init__(self, content: str, type: str):
        self.content = content
        self.type = type
        self.output = None
        self.plots = []


class SSHPythonRuntime(IRuntime):
    """
    Remote python runtime, handled as an interactive python shell via SSH.

    Report is generated as a markdown file with the code snippets and their outputs.
    """

    _saveplot__path_regex = r"(?<=\.savefig\([\'\"]).+(?=[\'\"]\))"

    def __init__(
        self, username: str, password: str, host: str = "127.0.0.1", port: int = 22
    ):
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(
            hostname=host, username=username, password=password, port=port
        )

        self._shell = self._ssh.invoke_shell()
        self._execute_command("python")
        self._execute_command("import os")  # Used for plots saving confirmation

        self._cells: list[_SSHPythonRuntimeCell] = []

    def __del__(self):
        self._shell.close()
        self._ssh.close()

    def add_description(self, description: str) -> int:
        self._cells.append(_SSHPythonRuntimeCell(description, "description"))
        return len(self._cells) - 1

    def add_code(self, code: str) -> int:
        # Replace complex path to simple one
        matches = re.findall(self._saveplot__path_regex, code)
        for match in matches:
            code = code.replace(match, match.split("/")[-1])

        if ".show()" in code:
            code = code.replace(".show()", f".savefig('{uuid.uuid4()}.png')")

        self._cells.append(_SSHPythonRuntimeCell(code, "code"))
        return len(self._cells) - 1

    def remove_cell(self, cell_index: int = -1) -> None:
        del self._cells[cell_index]

    def execute_cell(self, cell_index: int = -1) -> None:
        cell = self._cells[cell_index]
        if cell.type != "code":
            return

        commands = cell.content.split("\n")
        output = ""
        out_plots = []
        for c in commands:
            stream, plots = self._execute_command(c)
            stream = stream.strip()
            if stream != "":
                output += stream + "\n"
            if plots != []:
                out_plots += plots

        self._cells[cell_index].output = output.strip()
        self._cells[cell_index].plots = out_plots

    def get_content(self, cell_index: int = -1) -> str:
        return self._cells[cell_index].content

    def get_cell_output(self, cell_index: int = -1) -> Union[str, None]:
        cell = self._cells[cell_index]
        if cell.type != "code":
            return None

        return cell.output

    def check_if_plot_in_output(self, cell_index: int = -1) -> bool:
        return self._cells[cell_index].plots != []

    def upload_file(self, local_path: str, dest_file_path: str) -> None:
        sftp_client = self._ssh.open_sftp()
        sftp_client.put(local_path, dest_file_path)
        sftp_client.close()

    def generate_report(self, dest_dir: str, filename: str) -> str:
        markdown = ""

        for i, cell in enumerate(self._cells):
            if cell.type == "description":
                markdown += cell.content + "\n\n"
            else:
                markdown += f"```python\n{cell.content.strip()}\n```\n"
                if cell.output is not None:
                    markdown += f"```python\n# Output:\n{cell.output}\n```\n"
                for plot in cell.plots:
                    markdown += f"![{plot}]({plot})\n"
                    self._download_file(plot, f"{dest_dir}/{plot}")

        markdown_path = f"{dest_dir}/{filename}.md"

        with open(markdown_path, "w") as f:
            f.write(markdown)

        return markdown_path

    def _download_file(self, remote_path: str, local_path: str) -> None:
        sftp_client = self._ssh.open_sftp()
        sftp_client.get(remote_path, local_path)
        sftp_client.close()

    def _execute_command(self, command: str) -> Tuple[str, List[str]]:
        """
        Execute the given command in the remote shell.

        Returns:
            All output streams (both stdout and stderr) of the command.
            If the command saves a plots, the filenames are returned as well.
        """

        command = command.strip("\n")
        self._shell.send(command + "\n")

        # Check if command saves a plot and extract the filename
        filenames = re.findall(self._saveplot__path_regex, command)

        output_raw = ""
        self._shell.recv(len(command) + 1)
        while not output_raw.endswith(">>> "):
            output_raw += self._shell.recv(1024).decode("utf-8")

        for filename in filenames:
            test_plot_command = f"os.path.exists('{filename}')\n"
            self._shell.send(test_plot_command)
            retval = ""
            self._shell.recv(len(test_plot_command) + 1)
            while not retval.endswith(">>> "):
                retval += self._shell.recv(1024).decode("utf-8")
            if retval.strip() == "False":
                filenames.remove(filename)

        output = output_raw.replace(">>> ", "")

        return output, filenames
