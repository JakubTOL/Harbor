from PySide6.QtWidgets import QMenu, QInputDialog, QMessageBox, QApplication
from PySide6.QtGui import QAction
from pathlib import Path
from functools import partial
import os
import shutil
import sys
import subprocess


class ExplorerController:

    def __init__(self, state, fs_service, view, favorites_manger):
        """
        Initialize the ExplorerController.

        Args:
            state: The ExplorerState instance holding current explorer state.
            fs_service: The FileSystemService instance for filesystem operations.
            view: The view (typically ExplorerWindow) for UI updates.
        """
        self.state = state
        self.fs = fs_service
        self.view = view
        self.favorites = favorites_manger

    # -----------------------------
    # NAVIGATION CORE
    # -----------------------------

    def set_current_path(self, path: str):
        """
        Set the current path in the explorer, update state and view.

        Args:
            path (str): The filesystem path to set as current.
        """
        if not self.fs.exists(path):
            return

        self.state.current_path = path

        index = self.fs.index(path)

        self.view.update_path(index, path)

    def go_up(self):
        """
        Navigate to the parent directory of the current path.
        """
        parent = str(Path(self.state.current_path).parent)
        self.set_current_path(parent)

    def go_home(self):
        """
        Navigate to the home directory of the user.
        """
        self.set_current_path(str(Path.home()))

    def refresh(self):
        """
        Refresh the filer explorer view for the current directory.
        """
        current = self.state.current_path
        self.fs.model.setRootPath("")
        self.set_current_path(current)

    # -----------------------------
    # UI EVENTS
    # -----------------------------

    def on_tree_clicked(self, index: int ):
        """
        Handle event when a column view item is clicked.

        Args:
            index (int): The column view item index.
        """
        path = self.fs.file_path(index)
        if self.fs.is_dir(path):
            self.set_current_path(path)

    def on_column_clicked(self, index: int):
        """
        Handle event when a column view item is clicked.

        Args:
            index (int): The model index of the clicked item.
        """
        path = self.fs.file_path(index)
        if self.fs.is_dir(path):
            self.set_current_path(path)

    def on_double_clicked(self, index: int):
        """
        Handle event when item is double-clicked.

        Args:
            index (int): The model index of the clicked item.
        """
        path = self.fs.file_path(index)

        if self.fs.is_dir(path):
            self.set_current_path(path)
        else:
            self.fs.open_file(self.view, path)

    # -----------------------------
    # CONTEXT MENU
    # -----------------------------

    def show_context_menu(self, widget, index, point, directory_mode: bool = False):
        """
        Display the context menu for a file or directory.

        Args:
            widget: The widget where the context menu is requested.
            index: The model index for the item.
            point: The QPoint to display the menu.
            directory_mode (bool): If True, shows directory-only actions.
        """

        menu = QMenu(widget)
        path = self.fs.file_path(index)

        def make_action(text, callback):
            action = QAction(text, widget)
            action.triggered.connect(callback)
            return action

        # ------------------------------------------------------------------
        # Action registry
        # ------------------------------------------------------------------

        actions = {
            "open_native": make_action("Open in native", partial(self.open_item_in_native, index)),
            "copy_path": make_action("Copy as path", partial(self.copy_item_as_path, index)),
            "rename": make_action("Rename", partial(self.rename_item, index)),
            "new_file": make_action( "New File", partial(self.create_new_file, index)),
            "new_folder": make_action("New Folder", partial(self.create_new_folder, index)),
            "delete": make_action("Delete",partial(self.delete_item, index)),
        }

        # ------------------------------------------------------------------
        # Favorites section (directories only)
        # ------------------------------------------------------------------

        if self.fs.is_dir(path):
            is_favorite = self.favorites.is_favorite(path)

            favorite_action = make_action(
                "Remove from Favorites" if is_favorite else "Add to Favorites",
                partial(
                    self.remove_from_favorites if is_favorite
                    else self.add_to_favorites,
                    path
                )
            )

            menu.addSeparator()
            menu.addAction(favorite_action)
            menu.addSeparator()

        # ------------------------------------------------------------------
        # Menu layouts
        # None = separator
        # ------------------------------------------------------------------

        directory_layout = [
            "open_native",
            "copy_path",
            None,
            "new_file",
            "new_folder",
        ]

        default_layout = [
            "open_native",
            "copy_path",
            None,
            "rename",
            "new_file",
            "new_folder",
            None,
            "delete",
        ]

        layout = directory_layout if directory_mode else default_layout

        # ------------------------------------------------------------------
        # Render menu
        # ------------------------------------------------------------------

        for item in layout:
            if item is None:
                menu.addSeparator()
            else:
                menu.addAction(actions[item])

        menu.exec(widget.viewport().mapToGlobal(point))

    # -----------------------------
    # CONTEXT MENU ACTIONS
    # -----------------------------

    def open_item_in_native(self, index: int):
        """
        Open the selected file or directory in the native file browser.

        Args:
            index (int): The model index for the item to open.
        """
        path = self.fs.file_path(index)
        # If it's a file, open its parent dir and select the file where possible
        target_path = path
        is_file = os.path.isfile(path)
        if is_file:
            dir_path = os.path.dirname(path)
        else:
            dir_path = path

        try:
            if sys.platform.startswith("darwin"):  # macOS: highlight the item using -R if it's a file
                if is_file:
                    subprocess.run(['open', '-R', path], check=True)
                else:
                    subprocess.run(['open', dir_path], check=True)
            elif os.name == "nt":  # Windows: explorer with /select, for files
                """if is_file:
                    # subprocess.run(['explorer', '/select,', os.path.normpath(path)], check=True)
                    os.startfile(dir_path)
                else:
                    os.startfile(dir_path)"""
                os.startfile(dir_path)
            else:  # Linux: xdg-open to the folder
                subprocess.run(['xdg-open', dir_path], check=True)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to open in native file browser:\n{e}")

    def copy_item_as_path(self, index: int):
        """
        Copy focused item path to system clipboard.

        Args:
            index (int): The model index for the item to copy.
        """
        path = self.fs.file_path(index)

        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(path)

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to copy item path to clipboard:\n{e}"
            )


    def rename_item(self, index: int):
        """
        Rename a file or folder via an input dialog.

        Args:
            index (int): The model index for the item to rename.
        """
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

    def create_new_file(self, index: int):
        """
        Create a new file in the selected directory.

        Args:
            index (int): The model index representing directory or file.
        """
        dir_path = self.fs.file_path(index)
        if not self.fs.is_dir(dir_path):  # If it's a file, get its parent
            dir_path = os.path.dirname(dir_path)
        new_file, ok = QInputDialog.getText(
            self.view, "New File", "Enter file name with extension:"
        )
        if ok and new_file:
            new_path = os.path.join(dir_path, new_file)
            try:
                open(new_path, "w").close()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self.view, "Create File Failed", str(e))

    def create_new_folder(self, index: int):
        """
        Create a new folder in the selected directory.

        Args:
            index (int): The model index representing directory.
        """
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

    def delete_item(self, index: int):
        """
        Delete the selected file or folder after confirmation via input dialog.

        Args:
            index (int): The model index representing directory.
        """
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

    # -----------------------------
    # FAVORITES
    # -----------------------------

    def add_to_favorites(self, path):
        """
        Add the specified directory path to favorites.

        Args:
            path (str): Directory path to add.
        """
        self.favorites.add_favorite(path)
        if hasattr(self.view, "update_favorites_menu"):
            self.view.update_favorites_menu()  # Method you'll add in the view

    def remove_from_favorites(self, path):
        """
        Remove the specified directory path from favorites.

        Args:
            path (str): Directory path to remove.
        """
        self.favorites.remove_favorite(path)
        if hasattr(self.view, "update_favorites_menu"):
            self.view.update_favorites_menu()