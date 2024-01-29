import os
import re
import uuid
from typing import List, Tuple, Union

import paramiko

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
        """
        Initializes the SSHPythonRuntime object.

        Args:
            username (str): The username for SSH connection.
            password (str): The password for SSH connection.
            host (str, optional): The host IP address. Defaults to "127.0.0.1".
            port (int, optional): The SSH port number. Defaults to 22.

        Returns:
            None
        """
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
        """
        Closes the SSH connection and the shell when the object is destroyed.
        """
        self._shell.close()
        self._ssh.close()

    def set_report_title(self, title: str) -> None:
        """
        Sets the title of the report.

        Args:
            title (str): The title of the report.

        Returns:
            None
        """
        self._cells.insert(
            0, _SSHPythonRuntimeCell("content", title + "\n=============")
        )

    def add_description(self, description: str) -> int:
        """
        Adds a description to the SSH Python runtime.

        Args:
            description (str): The description to be added.

        Returns:
            int: The index of the added description in the runtime's cells.
        """
        self._cells.append(_SSHPythonRuntimeCell(description, "description"))
        return len(self._cells) - 1

    def add_code(self, code: str) -> int:
        """
        Adds code to the SSH Python runtime.

        Args:
            code (str): The code to be added.

        Returns:
            int: The index of the added code in the runtime's cells.
        """
        # Replace complex path to simple one
        matches = re.findall(self._saveplot__path_regex, code)
        for match in matches:
            code = code.replace(match, match.split("/")[-1])

        if ".show()" in code:
            code = code.replace(".show()", f".savefig('{uuid.uuid4()}.png')")

        self._cells.append(_SSHPythonRuntimeCell(code, "code"))
        return len(self._cells) - 1

    def remove_cell(self, cell_index: int = -1) -> None:
        """
        Removes a cell from the SSH Python runtime.

        Args:
            cell_index (int, optional): The index of the cell to be removed. Defaults to -1.

        Returns:
            None
        """
        del self._cells[cell_index]

    def execute_cell(self, cell_index: int = -1) -> None:
        """
        Executes a cell in the SSH Python runtime.

        Args:
            cell_index (int, optional): The index of the cell to be executed. Defaults to -1.

        Returns:
            None
        """
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
        """
        Gets the content of a cell in the SSH Python runtime.

        Args:
            cell_index (int, optional): The index of the cell. Defaults to -1.

        Returns:
            str: The content of the cell.
        """
        return self._cells[cell_index].content

    def get_cell_output_stream(self, cell_index: int = -1) -> Union[str, None]:
        """
        Gets the output stream of a cell in the SSH Python runtime.

        Args:
            cell_index (int, optional): The index of the cell. Defaults to -1.

        Returns:
            Union[str, None]: The output stream of the cell, or None if the cell is not a code cell.
        """
        cell = self._cells[cell_index]
        if cell.type != "code":
            return None

        return cell.output

    def check_if_plot_in_output(self, cell_index: int = -1) -> bool:
        """
        Checks if a plot is included in the output of a cell in the SSH Python runtime.

        Args:
            cell_index (int, optional): The index of the cell. Defaults to -1.

        Returns:
            bool: True if a plot is included in the output, False otherwise.
        """
        return self._cells[cell_index].plots != []

    def upload_file(self, local_path: str, dest_file_path: str) -> None:
        """
        Uploads a file from the local machine to the SSH Python runtime.

        Args:
            local_path (str): The local path of the file to be uploaded.
            dest_file_path (str): The destination path of the file in the SSH Python runtime.

        Returns:
            None
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError("File does not exist")

        sftp_client = self._ssh.open_sftp()
        sftp_client.put(local_path, dest_file_path)
        sftp_client.close()

    def generate_report(self, dest_dir: str, filename: str) -> str:
        """
        Generates a report with code snippets and their outputs.

        Args:
            dest_dir (str): The destination directory for the report.
            filename (str): The filename of the report.

        Returns:
            str: The path of the generated markdown report.
        """
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
        """
        Downloads a file from the SSH Python runtime to the local machine.

        Args:
            remote_path (str): The remote path of the file in the SSH Python runtime.
            local_path (str): The local path of the file to be downloaded.

        Returns:
            None
        """
        sftp_client = self._ssh.open_sftp()
        sftp_client.get(remote_path, local_path)
        sftp_client.close()

    def _execute_command(self, command: str) -> Tuple[str, List[str]]:
        """
        Executes a command in the remote shell.

        Args:
            command (str): The command to be executed.

        Returns:
            Tuple[str, List[str]]: The output streams (stdout and stderr) of the command,
            and the filenames of any saved plots.
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
