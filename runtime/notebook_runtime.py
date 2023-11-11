import requests
import os
import nbformat
import nbconvert
import uuid
import datetime
import json
from websocket import create_connection


class NotebookRuntime:
    """
    Class managing the Jupyter Notebook via REST API (kernel management) and WebSocket (execution).

    Notebook is fully edited locally (with nbformat package) and single cells are executed on the Jupyter Server via WebSockets.
    """

    _ws_username = "username"
    _ws_jupyter_message_version = "5.3"

    def __init__(self, token: str, host: str = "127.0.0.1", port: int = 8888):
        self._base_url = f"http://{host}:{port}/api"
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        self._notebook = nbformat.v4.new_notebook()
        self._kernel_id = self._start_kernel()
        self._ws_session = uuid.uuid4().hex

        self._ws = create_connection(
            f"ws://{host}:{port}/api/kernels/{self._kernel_id}/channels",
            header={"Authorization": f"token {token}"},
        )

    def __del__(self):
        self._session.close()
        self._ws.close()

    def add_markdown_cell(self, content: str) -> None:
        """Adds a markdown cell to the notebook."""

        self._notebook.cells.append(nbformat.v4.new_markdown_cell(content))

    def add_code_cell(self, content: str) -> None:
        """Adds a code cell to the notebook."""

        self._notebook.cells.append(nbformat.v4.new_code_cell(content))

    def get_cell_output(self, idx: int = -1) -> str:
        """Returns the output of the selected cell."""

        return self._notebook.cells[idx].outputs

    def remove_cell(self, idx: int = -1) -> None:
        """Removes the selected cell from the notebook."""

        del self._notebook.cells[idx]

    def reset_outputs(self) -> None:
        """Resets the outputs of all cells."""

        for cell in self._notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []

    def execute_cell(self, idx: int = -1) -> None:
        """Executes the selected cell."""

        if self._notebook.cells[idx].cell_type == "code":
            self._notebook.cells[idx] = self._execute_cell(self._notebook.cells[idx])

    def generate_pdf(self, output_path: str) -> None:
        """Generates a pdf from the notebook."""

        exporter = nbconvert.PDFExporter()
        body, resources = exporter.from_notebook_node(self._notebook)

        with open(output_path, "wb") as f:
            f.write(body)

    def upload_file(self, local_path: str, dest_file_path: str) -> None:
        """
        Uploads the data files to the Jupyter Server (for kernel access).

        Parameters:
            local_path: The path to the dataset on the local machine.
            
        """

        assert os.path.exists(local_path), "Dataset file does not exist"

        filename = local_path.split("/")[-1]
        path = f"{self._remote_data_dir}{filename}"
        url = f"{self._base_url}/contents/{path}"

        with open(local_path, "rb") as f:
            body = {
                "name": filename,
                "path": path,
                "type": "file",
                "format": "text",
                "content": f.read().decode("utf-8"),
            }
            response = self._session.put(url, json=body)

        response.raise_for_status()

    def _execute_cell(
        self, cell: nbformat.notebooknode.NotebookNode
    ) -> nbformat.notebooknode.NotebookNode:
        """Executes the given cell in IPython kernel and save the result to the cell."""

        # TODO: Set timeout

        # Clear previous outputs
        cell["outputs"] = [] 

        content = {
            "code": cell.source,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False,
            "stop_on_error": True,
        }

        msg = self._create_ws_message("execute_request", content)
        self._ws.send(json.dumps(msg))

        idle_signal_received = False
        execute_reply_received = False

        while not idle_signal_received or not execute_reply_received:
            response = json.loads(self._ws.recv())

            if response["parent_header"]["msg_id"] != msg["msg_id"]:
                # Message not related to the execution request
                continue

            match response["msg_type"]:
                case "status" if response["content"]["execution_state"] == "idle":
                    idle_signal_received = True
                case "execute_reply":
                    execute_reply_received = True
                    cell["execution_count"] = response["content"]["execution_count"]
                case "stream" | "display_data" | "execute_result" | "error":
                    cell["outputs"].append(
                        {
                            **response["content"],
                            "output_type": response["msg_type"],
                        }
                    )
                case _:
                    pass

        return cell

    def _create_ws_message(self, msg_type: str, content: dict) -> dict:
        header = {
            "msg_id": uuid.uuid4().hex,  # Must be unique per message
            "username": self._ws_username,  # Useful in collaborative settings where multiple users may be interacting with the same kernel simultaneously, so that frontends can label the various messages in a meaningful way.
            "session": self._ws_session,  # A client session id, in message headers from a client, should be unique among all clients connected to a kernel. When a client reconnects to a kernel, it should use the same client session id in its message headers. When a client restarts, it should generate a new client session id.
            "data": datetime.datetime.now().isoformat(),
            "msg_type": msg_type,
            "version": self._ws_jupyter_message_version,  # The version of the Jupyter messaging protocol that the message conforms to. This is distinct from the version of the overall Jupyter protocol, which is the version of the overall protocol that the message conforms to. The version of the overall protocol is specified in the outermost header of the message.
        }
        msg = {
            "header": header,
            "msg_id": header["msg_id"],  # Python API extension
            "msg_type": msg_type,  # Python API extension
            "parent_header": {},  # We assume this class is not providing any responses
            "metadata": {},
            "content": content,
            "buffers": [],
            "channel": "shell",  # Value not in Jupyter messaging protocol specification. Added by Jupyter Server (since one endpoint represents multiple channels of interal communication).
        }
        return msg

    def _start_kernel(self) -> str:
        """Starts the kernel on the Jupyter Server."""

        url = f"{self._base_url}/kernels"
        response = self._session.post(url, json={"name": "python3"})
        response.raise_for_status()
        return response.json()["id"]

    def _restart_kernel(self) -> None:
        """Restarts the kernel on the Jupyter Server."""

        url = f"{self._base_url}/kernels/{self._kernel_id}/restart"
        response = self._session.post(url)
        response.raise_for_status()
