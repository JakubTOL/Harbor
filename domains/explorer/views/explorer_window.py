from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QSplitter, QListView
from PySide6.QtCore import Qt

from core.constants import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

from domains.explorer.models.explorer_state import ExplorerState
from domains.explorer.services.filesystem_service import FileSystemService
from domains.explorer.controllers.explorer_controller import ExplorerController

from domains.explorer.widgets.explorer_tree import ExplorerTree
from domains.explorer.widgets.finder_column_view import FinderColumnView
from domains.explorer.widgets.breadcrumb_bar import BreadcrumbBar
from domains.explorer.widgets.navigation_toolbar import NavigationToolbar


class ExplorerWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # -------------------------
        # CORE LAYERS
        # -------------------------

        self.state = ExplorerState(current_path=str(Path.home()))
        self.fs = FileSystemService()

        self.controller = ExplorerController(
            self.state,
            self.fs,
            self
        )

        self._build_ui()

        self.controller.set_current_path(self.state.current_path)

    # -------------------------
    # UI
    # -------------------------

    def _build_ui(self):

        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)

        # Breadcrumb
        self.breadcrumb = BreadcrumbBar(self.controller.set_current_path)
        layout.addWidget(self.breadcrumb)

        # Stack
        self.stack = QStackedWidget()

        # TREE MODE
        tree_page = QWidget()
        tree_layout = QVBoxLayout(tree_page)

        splitter = QSplitter(Qt.Horizontal)

        """self.tree = ExplorerTree(
            self.fs.model,
            self.controller.on_tree_clicked
        )"""
        self.tree = ExplorerTree(
            self.fs.model,
            self.controller.on_tree_clicked,
            self.controller
        )

        self.tree.setMinimumWidth(300)

        # SECOND COLUMN WIDGET: (here, as an example, a QListView showing list of files in selected directory)
        self.detail_list = QListView()
        self.detail_list.setModel(self.fs.model)
        self.detail_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.detail_list.customContextMenuRequested.connect(self.show_list_context_menu)

        splitter.addWidget(self.tree)
        splitter.addWidget(self.detail_list)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        tree_layout.addWidget(splitter)
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

        self.stack.addWidget(tree_page)
        self.stack.addWidget(finder_page)

        layout.addWidget(self.stack)

        # Toolbar
        self.addToolBar(NavigationToolbar(self, self.controller))

    # -------------------------
    # CALLED BY CONTROLLER
    # -------------------------

    def update_path(self, index, path: str):

        self.breadcrumb.set_path(path)

        self.tree.setRootIndex(index)
        self.column.setRootIndex(index)

        self.statusBar().showMessage(path)

    def show_list_context_menu(self, point):
        index = self.detail_list.indexAt(point)
        if not index.isValid():
            return
        self.controller.show_context_menu(self.detail_list, index, point)

    # -------------------------
    # VIEW MODES
    # -------------------------

    def set_mode(self, index: int):
        self.stack.setCurrentIndex(index)

    def show_details_for_index(self, index):
        if self.fs.model.isDir(index):
            self.detail_list.setRootIndex(index)
        else:
            # Optionally set to parent directory or clear
            parent = index.parent()
            self.detail_list.setRootIndex(parent)
