from pathlib import Path


class ExplorerController:

    def __init__(self, state, fs_service, view):
        self.state = state
        self.fs = fs_service
        self.view = view

    # -----------------------------
    # NAVIGATION CORE
    # -----------------------------

    def set_current_path(self, path: str):

        if not self.fs.exists(path):
            return

        self.state.current_path = path

        index = self.fs.index(path)

        self.view.update_path(index, path)

    def go_up(self):
        parent = str(Path(self.state.current_path).parent)
        self.set_current_path(parent)

    def go_home(self):
        self.set_current_path(str(Path.home()))

    def refresh(self):
        current = self.state.current_path
        self.fs.model.setRootPath("")
        self.set_current_path(current)

    # -----------------------------
    # UI EVENTS
    # -----------------------------

    def on_tree_clicked(self, index):
        path = self.fs.file_path(index)
        if self.fs.is_dir(path):
            self.set_current_path(path)

    def on_column_clicked(self, index):
        path = self.fs.file_path(index)
        if self.fs.is_dir(path):
            self.set_current_path(path)

    def on_double_clicked(self, index):
        path = self.fs.file_path(index)

        if self.fs.is_dir(path):
            self.set_current_path(path)
        else:
            self.fs.open_file(self.view, path)