from pathlib import Path
from PySide6.QtWidgets import QMenu, QInputDialog, QMessageBox
from PySide6.QtGui import QAction
import os
import shutil


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

    # --------
    # CONTEXT MENU
    # --------

    def show_context_menu(self, widget, index, point):
        menu = QMenu(widget)
        rename_action = QAction("Rename", widget)
        new_file_action = QAction("New File", widget)
        new_folder_action = QAction("New Folder", widget)
        delete_action = QAction("Delete", widget)

        rename_action.triggered.connect(lambda: self.rename_item(index))
        new_file_action.triggered.connect(lambda: self.create_new_file(index))
        new_folder_action.triggered.connect(lambda: self.create_new_folder(index))
        delete_action.triggered.connect(lambda: self.delete_item(index))

        menu.addAction(rename_action)
        menu.addAction(new_file_action)
        menu.addAction(new_folder_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec(widget.viewport().mapToGlobal(point))

    def rename_item(self, index):
        old_path = self.fs.file_path(index)
        base_dir = os.path.dirname(old_path)
        old_name = os.path.basename(old_path)

        new_name, ok = QInputDialog.getText(
            self.view, "Rename", f"Rename '{old_name}' to:"
        )
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(base_dir, new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self.view, "Rename Failed", str(e))

    def create_new_file(self, index):
        dir_path = self.fs.file_path(index)
        if not self.fs.is_dir(dir_path):  # If it's a file, get its parent
            dir_path = os.path.dirname(dir_path)
        new_file, ok = QInputDialog.getText(
            self.view, "New File", "Enter file name:"
        )
        if ok and new_file:
            new_path = os.path.join(dir_path, new_file)
            try:
                open(new_path, "w").close()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self.view, "Create File Failed", str(e))

    def create_new_folder(self, index):
        dir_path = self.fs.file_path(index)
        if not self.fs.is_dir(dir_path):
            dir_path = os.path.dirname(dir_path)
        new_folder, ok = QInputDialog.getText(
            self.view, "New Folder", "Enter folder name:"
        )
        if ok and new_folder:
            new_path = os.path.join(dir_path, new_folder)
            try:
                os.makedirs(new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self.view, "Create Folder Failed", str(e))

    def delete_item(self, index):
        path = self.fs.file_path(index)
        if not os.path.exists(path):
            return

        msg = (f"Delete '{os.path.basename(path)}'?\n"
               f"File will be removed permanently without moving to bin!\n"
               f"This cannot be undone.")
        if os.path.isdir(path):
            msg += "\nAll contents will be deleted."

        reply = QMessageBox.question(
            self.view,
            "Delete",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self.view, "Delete Failed", str(e))
