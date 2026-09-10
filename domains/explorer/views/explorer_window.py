from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget, QSplitter, QListView,
                               QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt
import os

from domains.explorer.models.explorer_state import ExplorerState
from domains.explorer.services.filesystem_service import FileSystemService
from domains.explorer.controllers.explorer_controller import ExplorerController

from domains.explorer.widgets.explorer_tree import ExplorerTree
from domains.explorer.widgets.finder_column_view import FinderColumnView
from domains.explorer.widgets.breadcrumb_bar import BreadcrumbBar
from domains.explorer.widgets.file_metadata_panel import FileMetadataPanel


class ExplorerTab(QWidget):
    """
    A single tab containing a full explorer view (breadcrumbs, tree/finder, metadata).
    This object acts as the 'view' passed to ExplorerController.
    """

    def __init__(self, parent_window, initial_path: str, favorites_manager):
        """
        parent_window: the main ExplorerWindow instance (used for shared UI like search results)
        initial_path: starting directory for this tab
        favorites_manager: shared FavoritesManager instance
        """
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.initial_path = initial_path or str(Path.home())
        self.favorites_manager = favorites_manager

        # Per-tab model/state/controller
        self.state = ExplorerState(current_path=self.initial_path)
        self.fs = FileSystemService()
        self.controller = ExplorerController(
            self.state,
            self.fs,
            self,
            self.favorites_manager
        )

        self._build_ui()
        # Navigate to initial path
        self.controller.set_current_path(self.state.current_path)

    def _build_ui(self):
        root = QWidget()
        # We'll keep self as the root for the tab
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Breadcrumb
        self.breadcrumb = BreadcrumbBar(self.controller.set_current_path)
        layout.addWidget(self.breadcrumb)

        # Stack (tree/finder)
        self.stack = QStackedWidget()

        # TREE MODE
        tree_page = QWidget()
        tree_layout = QVBoxLayout(tree_page)

        splitter = QSplitter(Qt.Horizontal)

        self.tree = ExplorerTree(
            self.fs.model,
            self.controller.on_tree_clicked,
            self.controller
        )
        self.tree.setMinimumWidth(300)

        # SECOND COLUMN WIDGET: QListView as before
        self.detail_list = QListView()
        self.detail_list.setModel(self.fs.model)
        self.detail_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.detail_list.customContextMenuRequested.connect(self.show_list_context_menu)
        self.detail_list.doubleClicked.connect(self.controller.on_double_clicked)

        splitter.addWidget(self.tree)
        splitter.addWidget(self.detail_list)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        tree_layout.addWidget(splitter)

        self.metadata_panel = FileMetadataPanel(max_height=32)
        tree_layout.addWidget(self.metadata_panel)

        self.tree.clicked.connect(self.show_details_for_index)

        # FINDER MODE
        finder_page = QWidget()
        finder_layout = QVBoxLayout(finder_page)

        self.column = FinderColumnView(
            self.fs.model,
            self.controller.on_column_clicked,
            self.controller.on_double_clicked,
            self.controller
        )

        finder_layout.addWidget(self.column)

        self.metadata_panel_finder = FileMetadataPanel(max_height=44)
        finder_layout.addWidget(self.metadata_panel_finder)

        self.column.clicked.connect(self.update_finder_metadata_panel)
        self.column.doubleClicked.connect(self.update_finder_metadata_panel)

        self.stack.addWidget(tree_page)
        self.stack.addWidget(finder_page)

        layout.addWidget(self.stack)

    # Methods expected by the controller (previously in ExplorerWindow)

    def update_path(self, index, path: str):
        """
        Update the view and UI to reflect the new path for this tab.
        """
        self.breadcrumb.set_path(path)

        self.tree.setRootIndex(index)
        self.column.setRootIndex(index)

        # If the main window has a status bar, show the current path
        if hasattr(self.parent_window, "statusBar"):
            self.parent_window.statusBar().showMessage(path)

        self.metadata_panel.set_path(path)

        # Notify main window so it can update the tab title/tooltip if needed
        if hasattr(self.parent_window, "update_tab_title_for_widget"):
            self.parent_window.update_tab_title_for_widget(self, path)

    def show_list_context_menu(self, point):
        index = self.detail_list.indexAt(point)
        if index.isValid():
            self.controller.show_context_menu(self.detail_list, index, point, directory_mode=False)
        else:
            dir_index = self.detail_list.rootIndex()
            self.controller.show_context_menu(self.detail_list, dir_index, point, directory_mode=True)

    def update_finder_metadata_panel(self, index):
        path = self.fs.model.filePath(index)
        self.metadata_panel_finder.set_path(path)

    def update_favorites_menu(self):
        """
        Called by controller (when favorites change) to refresh main toolbar favorites.
        Delegate to parent window which owns the toolbar.
        """
        if hasattr(self.parent_window, "update_favorites_menu"):
            self.parent_window.update_favorites_menu()

    def open_selected_in_native(self):
        """
        Called by parent window when global 'open in native' or shortcut is triggered.
        Determine selection in this tab and forward to controller.
        """
        current_index = self.stack.currentIndex()
        if current_index == 0:  # tree
            selected = self.tree.selectedIndexes()
            if selected:
                self.controller.open_item_in_native(selected[0])
        elif current_index == 1:
            selected = self.column.selectedIndexes()
            if selected:
                self.controller.open_item_in_native(selected[0])

    # Search results are displayed by the main window's dock; controllers call view.display_search_results()
    def display_search_results(self, results: list) -> None:
        """
        Proxy request to parent main window to render search results.
        """
        if hasattr(self.parent_window, "display_search_results"):
            self.parent_window.display_search_results(results)

    def set_mode(self, index: int):
        """
        Switch tree/finder for this tab.
        """
        self.stack.setCurrentIndex(index)

    def show_details_for_index(self, index):
        """
        Similar to ExplorerWindow.show_details_for_index but per-tab.
        """
        if self.fs.model.isDir(index):
            self.detail_list.setRootIndex(index)
        else:
            parent = index.parent()
            self.detail_list.setRootIndex(parent)
        path = self.fs.model.filePath(index)
        self.metadata_panel.set_path(path)
