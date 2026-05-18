import os
import sys
import subprocess
from PySide6.QtWidgets import QFileSystemModel, QMessageBox


class FileSystemService:

    def __init__(self):
        self.model = QFileSystemModel()
        self.model.setRootPath("")

    def index(self, path: str):
        return self.model.index(path)

    def file_path(self, index):
        return self.model.filePath(index)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)

    def open_file(self, parent, path: str):
        try:
            if sys.platform.startswith("darwin"):
                subprocess.call(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            else:
                subprocess.call(["xdg-open", path])

        except Exception as e:
            QMessageBox.critical(parent, "Error", str(e))