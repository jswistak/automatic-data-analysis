from abc import ABC, abstractmethod
from typing import Union


class IRuntime(ABC):
    """
    Class representing the analysis process.
    It takes the code snippets and allows to run them.
    Except the code itself, it also keeps the comments describing the whole process.

    Each separate input (both code and description blocks) is stored with the index, so that it can be easily referenced.
    Those blocks will be called cells.
    It is based on Jupyter Notebook design.
    """

    @abstractmethod
    def add_description(self, description: str) -> int:
        """
        Adds a cell with the description of the process.

        Returns:
            The index of the cell.
        """
        pass

    @abstractmethod
    def add_code(self, code: str) -> int:
        """
        Adds a cell with the code.

        Returns:
            The index of the cell.
        """
        pass

    @abstractmethod
    def remove_cell(self, cell_index: int) -> None:
        """
        Removes the cell with the given index.
        """
        pass

    @abstractmethod
    def execute_cell(self, cell_index: int) -> None:
        """
        Executes a cell with the given index, if it is a code cell. Otherwise, does nothing.
        Errors are also written to the output.
        """
        pass

    @abstractmethod
    def get_content(self, cell_index: int) -> str:
        """
        Returns the content of the cell with the given index.
        """
        pass

    @abstractmethod
    def get_cell_output(self, cell_index: int) -> Union[str, None]:
        """
        Returns the output of the cell with the given index, if it is a code cell. Otherwise, returns None.
        """
        pass

    @abstractmethod
    def check_if_plot_in_output(self, cell_index: int) -> bool:
        """
        Returns true if the output of the cell with the given index contains a plot.
        """
        pass

    @abstractmethod
    def upload_file(self, local_path: str, dest_file_path: str) -> None:
        """
        Uploads the data files for further use by runtime.

        Parameters:
            local_path: The path to the dataset on the local machine.
            dest_file_path: The path to the dataset on the remote machine.

        Returns:
            The absolute path to the uploaded file on the remote machine.
        """
        pass

    @abstractmethod
    def generate_report(self, dest_dir: str, filename: str) -> str:
        """
        Generates the report representing the analysis so far (including the code and the output it cell was executed).
        The typo of the file is determined by the runtime.

        Parameters:
            dest_dir: The directory where the report will be saved.
            filename: The name of the report file (without extension).
        """
        pass
