import requests
import os
import nbformat
import nbconvert
import uuid
import datetime
import json
from typing import Union
from websocket import create_connection
from runtime.iruntime import IRuntime


class NotebookRuntime(IRuntime):
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

    def add_description(self, description: str) -> int:
        self._notebook.cells.append(nbformat.v4.new_markdown_cell(description))
        return len(self._notebook.cells) - 1

    def add_code(self, code: str) -> int:
        self._notebook.cells.append(nbformat.v4.new_code_cell(code))
        return len(self._notebook.cells) - 1

    def remove_cell(self, cell_index: int = -1) -> None:
        del self._notebook.cells[cell_index]

    def execute_cell(self, cell_index: int = -1) -> None:
        if self._notebook.cells[cell_index].cell_type == "code":
            self._notebook.cells[cell_index] = self._execute_cell(
                self._notebook.cells[cell_index]
            )

    def get_content(self, cell_index: int = -1) -> str:
        return self._notebook.cells[cell_index].source

    def get_cell_output_stream(self, cell_index: int = -1) -> Union[str, None]:
        cell = self._notebook.cells[cell_index]
        if cell.cell_type != "code":
            return None

        out_stream = ""
        for output in cell.outputs:
            match output.output_type:
                case "stream":
                    out_stream += output.text.replace("\r", "")
                case "execute_result" | "display_data":
                    if output.data["text/plain"] and output.data["text/plain"] != "":
                        out_stream += output.data["text/plain"]
                case "error":
                    out_stream += output.ename + "\n"
                    out_stream += output.evalue + "\n"
                    out_stream += "\n".join(output.traceback)
                case _:
                    pass

        return out_stream

    def check_if_plot_in_output(self, cell_index: int = -1) -> bool:
        cell = self._notebook.cells[cell_index]
        if cell.cell_type != "code":
            return False

        for output in cell.outputs:
            if output.output_type == "display_data" and "image/png" in output.data:
                return True

    def upload_file(self, local_path: str, dest_file_path: str) -> None:
        if not os.path.exists(local_path):
            raise FileNotFoundError("File does not exist")

        filename = os.path.basename(dest_file_path)
        url = f"{self._base_url}/contents/{dest_file_path}"

        with open(local_path, "rb") as f:
            body = {
                "name": filename,
                "path": dest_file_path,
                "type": "file",
                "format": "text",
                "content": f.read().decode("utf-8"),
            }
            response = self._session.put(url, json=body)

        response.raise_for_status()

    def generate_report(self, dest_dir: str, filename: str) -> str:
        exporter = nbconvert.PDFExporter()
        body, resources = exporter.from_notebook_node(self._notebook)

        output_path = f"{dest_dir}/{filename}.pdf"
        with open(output_path, "wb") as f:
            f.write(body)
        return output_path

    def _execute_cell(
        self, cell: nbformat.notebooknode.NotebookNode
    ) -> nbformat.notebooknode.NotebookNode:
        """Executes the given cell in IPython kernel and save the result to the cell."""

        # TODO: Set timeout

        # Clear previous outputs
        cell.outputs = []

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
                    cell.execution_count = response["content"]["execution_count"]
                case "stream" | "display_data" | "execute_result" | "error":
                    cell.outputs.append(nbformat.v4.output_from_msg(response))
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
