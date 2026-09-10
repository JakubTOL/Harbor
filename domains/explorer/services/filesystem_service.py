import os
import sys
import subprocess
from PySide6.QtWidgets import QFileSystemModel, QMessageBox
from pathlib import Path


class FileSystemService:

    def __init__(self):
        """
        Initialize the file system service with a QFileSystemModel.
        Avoid calling setRootPath('') which can trigger a heavy scan of filesystem roots.
        """
        self.model = QFileSystemModel()
        # Use the user's home directory as a reasonable default root to avoid scanning the entire FS.
        self.model.setRootPath(str(Path.home()))

    def index(self, path: str):
        """
        Get the model index for a given filesystem path.

        Args:
            path (str): The filesystem path.

        Returns:
            QModelIndex: The model index.
        """
        return self.model.index(path)

    def file_path(self, index: int) -> str:
        """
        Get the file path from a model index.

        Args:
            index (int): The model index.

        Returns:
            str: The file or directory path.
        """
        return self.model.filePath(index)

    def exists(self, path: str) -> bool:
        """
        Check if a filesystem path exists.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return os.path.exists(path)

    def is_dir(self, path: str) -> bool:
        """
        Check if a path is a directory.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        return os.path.isdir(path)

    def open_file(self, parent, path: str):
        """
        Open a file using the default application for the current platform.

        Args:
            parent: THe parent widget for error dialogs.
            path (str): The path of the file to open.
        """
        try:
            if sys.platform.startswith("darwin"):
                subprocess.call(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            else:
                subprocess.call(["xdg-open", path])

        except Exception as e:
            QMessageBox.critical(parent, "Error", str(e))
