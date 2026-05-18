from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget

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

        self.tree = ExplorerTree(
            self.fs.model,
            self.controller.on_tree_clicked
        )

        tree_layout.addWidget(self.tree)

        # FINDER MODE
        finder_page = QWidget()
        finder_layout = QVBoxLayout(finder_page)

        self.column = FinderColumnView(
            self.fs.model,
            self.controller.on_column_clicked,
            self.controller.on_double_clicked
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

    # -------------------------
    # VIEW MODES
    # -------------------------

    def set_mode(self, index: int):
        self.stack.setCurrentIndex(index)