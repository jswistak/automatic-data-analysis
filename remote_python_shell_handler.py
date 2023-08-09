import paramiko
import re
from typing import Tuple, Union


class RemotePythonShellHandler:
    """
    Class handling the remote python shell connection.

    The remote python shell is persisted until the object is destroyed (or the connection breaks).
    """

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, username=username, password=password, port=port)

        self.shell = self.ssh.invoke_shell()
        self.execute("python")

    def __del__(self):
        self.ssh.close()

    def execute(
        self, command: str, simplify_output: bool = True
    ) -> Union[Tuple[str, str, str], str]:
        """
        Execute the given command in the remote shell.

        Parameters:
            command: The command to execute.
            simplify_output: Whether to simplify the output (return mixed stdout and stderr) or not (separate stdin, stdout and stderr).

        Examples:
            execute("ls -l")
            execute("cd /home/user")

        Returns:
            A tuple containing the stdin, stdout and stderr or a string containing the mixed stdout and stderr.
        """

        command = command.strip("\n")
        self.shell.send(command + "\n")

        output_raw = ""
        while not output_raw.endswith(">>> "):
            output_raw += self.shell.recv(1024).decode("utf-8")

        if simplify_output:
            return output_raw.replace(">>> ", "")

        stdout = []
        stderr = []
        error = False

        for line in output_raw.split("\n"):
            if str(line).startswith("Traceback"):
                error = True

            # get rid of 'coloring and formatting' special characters
            if error:
                stderr.append(
                    re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
                    .sub("", line)
                    .replace("\b", "")
                    .replace("\r", "")
                )
            else:
                stdout.append(
                    re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
                    .sub("", line)
                    .replace("\b", "")
                    .replace("\r", "")
                )

        stdout = "\n".join(stdout).strip("\n")
        stderr = "\n".join(stderr).strip("\n")
        return command, stdout, stderr

    def transfer_file(self, src_file_path: str, dest_file_path: str) -> None:
        """
        Moves the file from the local machine to the remote machine, to which the SSH connection is established.

        Parameters:
            src_file_path: The path to the file on the local machine.
            dest_file_path: The path to the file on the remote machine.
        """

        sftp_client = self.ssh.open_sftp()
        sftp_client.put(src_file_path, dest_file_path)
