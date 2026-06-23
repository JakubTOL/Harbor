from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QSplitter, QListView
from PySide6.QtCore import Qt

from core.constants import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

from domains.application.favorites_manager import FavoritesManager

from domains.explorer.models.explorer_state import ExplorerState
from domains.explorer.services.filesystem_service import FileSystemService
from domains.explorer.controllers.explorer_controller import ExplorerController

from domains.explorer.widgets.explorer_tree import ExplorerTree
from domains.explorer.widgets.finder_column_view import FinderColumnView
from domains.explorer.widgets.breadcrumb_bar import BreadcrumbBar
from domains.explorer.widgets.navigation_toolbar import NavigationToolbar
from domains.explorer.widgets.file_metadata_panel import FileMetadataPanel


class ExplorerWindow(QMainWindow):

    def __init__(self):
        """
        Initialize the explorer window, controller and UI.
        """
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # -------------------------
        # CORE LAYERS
        # -------------------------

        self.state = ExplorerState(current_path=str(Path.home()))
        self.fs = FileSystemService()
        self.favorites_manager = FavoritesManager()

        self.controller = ExplorerController(
            self.state,
            self.fs,
            self,
            self.favorites_manager
        )

        self._build_ui()

        self.controller.set_current_path(self.state.current_path)

    # -------------------------
    # UI
    # -------------------------

    def _build_ui(self):
        """
        Build the main UI layout and widgets.
        """

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
        self.detail_list.doubleClicked.connect(self.controller.on_double_clicked)
        # self.detail_list.clicked.connect(self.show_details_for_index)  # gets buggy with macOS touchapd

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

        # Toolbar
        self.toolbar = NavigationToolbar(self, self.controller, self.favorites_manager)  # Store as attribute for update
        self.addToolBar(self.toolbar)

    # -------------------------
    # CALLED BY CONTROLLER
    # -------------------------

    def update_path(self, index, path: str):
        """
        Update the view and UI to reflect the new path.

        Args:
            index: The model index for the directory.
            path: The current path as a string.
        """
        self.breadcrumb.set_path(path)

        self.tree.setRootIndex(index)
        self.column.setRootIndex(index)

        self.statusBar().showMessage(path)
        self.metadata_panel.set_path(path)

    def show_list_context_menu(self, point):
        """
        Show the context menu in the detail list view.

        Args:
            point: The QPoint where the menu should appear.
        """
        index = self.detail_list.indexAt(point)
        if index.isValid():  # On file/folder
            self.controller.show_context_menu(self.detail_list, index, point, directory_mode=False)
        else:  # On blank area: use the current directory displayed in the details pane
            dir_index = self.detail_list.rootIndex()
            self.controller.show_context_menu(self.detail_list, dir_index, point, directory_mode=True)

    def update_finder_metadata_panel(self, index):
        """
        Update the finder metadata panel.

        Args:
            index: The model index for the directory.
        """
        path = self.fs.model.filePath(index)
        self.metadata_panel_finder.set_path(path)

    def update_favorites_menu(self):
        """
        Update the Favorites menu in the navigation toolbar.

        Called whenever the list of favorites changes.
        """
        self.toolbar.update_favorites_menu()

    # -------------------------
    # VIEW MODES
    # -------------------------

    def set_mode(self, index: int):
        """
        Switches between view modes (tree and finder).

        Args:
            index: The model index of the view mode.
        """
        self.stack.setCurrentIndex(index)

    def show_details_for_index(self, index):
        """
        Show the list of files for the selected directory.

        Args:
            index: The selected QModelIndex .
        """
        if self.fs.model.isDir(index):
            self.detail_list.setRootIndex(index)
        else:
            # Optionally set to parent directory or clear
            parent = index.parent()
            self.detail_list.setRootIndex(parent)
        path = self.fs.model.filePath(index)
        self.metadata_panel.set_path(path)