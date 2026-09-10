from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QDockWidget,
                               QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt
import os

from core.constants import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

from domains.application.favorites_manager import FavoritesManager

from domains.explorer.views.explorer_tab import ExplorerTab

from domains.explorer.widgets.navigation_toolbar import NavigationToolbar


class ExplorerWindow(QMainWindow):

    def __init__(self):
        """
        Initialize the explorer main window with tab support.
        """
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # Shared favorites manager
        self.favorites_manager = FavoritesManager()

        # Tab widget as central area
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

        # choose tab naming mode: "iterative" or "basename"
        self.tab_naming_mode = "basename"

        # Toolbar - pass window to toolbar so it can call back to active tab
        self.toolbar = NavigationToolbar(self, self.favorites_manager)
        self.addToolBar(self.toolbar)

        # SEARCH RESULTS DOCK (shared)
        self.search_results_dock = QDockWidget("Search Results", self)
        self.search_results_list = QListWidget()
        self.search_results_list.itemClicked.connect(self._on_search_result_clicked)
        self.search_results_dock.setWidget(self.search_results_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.search_results_dock)
        self.search_results_dock.hide()  # Hidden by default

        # Create initial tab at home directory
        initial_path = str(Path.home())
        self.create_new_tab(initial_path)

    # -------- Tab management --------

    def create_new_tab(self, path: str = None, title: str = None):
        """
        Create a new explorer tab. If path is None uses home directory.
        Uses basename naming mode: tab label = os.path.basename(path) or full path.
        """
        path = path or str(Path.home())

        # Decide title: explicit title wins, otherwise basename of path
        if title is None:
            tab_title = os.path.basename(path) or path
        else:
            tab_title = title

        tab = ExplorerTab(self, path, self.favorites_manager)
        idx = self.tabs.addTab(tab, tab_title)
        # Store full path as tooltip so user can see the complete location
        self.tabs.setTabToolTip(idx, path)
        self.tabs.setCurrentIndex(idx)

    def _on_tab_close_requested(self, index: int):
        # Prevent closing last tab - keep at least one
        if self.tabs.count() <= 1:
            return
        self.tabs.removeTab(index)

    def close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx >= 0 and self.tabs.count() > 1:
            self.tabs.removeTab(idx)

    def _on_tab_changed(self, index: int):
        """
        Called when user switches tab. Update toolbar/favorites status if needed.
        """
        # Optionally, update window title/status bar
        active = self.get_active_tab()
        if active:
            # Update status bar message to reflect active tab path
            if hasattr(self, "statusBar"):
                # Show current_path stored in tab.state
                self.statusBar().showMessage(active.state.current_path)

        # Refresh favorites menu so it shows actions that target the active tab
        self.update_favorites_menu()

    def update_tab_title_for_widget(self, tab_widget, path: str):
        """
        Called by an ExplorerTab when its path changes.
        Updates tab text based on tab_naming_mode and always updates tooltip.
        """
        idx = self.tabs.indexOf(tab_widget)
        if idx == -1:
            return

        # Update tooltip (always show full path)
        self.tabs.setTabToolTip(idx, path)

        # Update visible label only for basename mode (iterative keeps original Tab N).
        if self.tab_naming_mode == "basename":
            title = os.path.basename(path) or path
            self.tabs.setTabText(idx, title)

    def get_active_tab(self):
        widget = self.tabs.currentWidget()
        return widget

    def get_active_controller(self):
        tab = self.get_active_tab()
        if tab and hasattr(tab, "controller"):
            return tab.controller
        return None

    # -------- Delegation for toolbar actions and search --------

    def perform_search(self, query: str):
        """
        Called by the toolbar/search widget; delegate to active tab's controller.
        """
        ctrl = self.get_active_controller()
        if ctrl:
            ctrl.perform_search(query)

    def display_search_results(self, results: list) -> None:
        """
        Render results in shared search dock. Clicks are handled and delegated to the active tab.
        """
        self.search_results_list.clear()

        if not results:
            self.search_results_dock.hide()
            return

        self.search_results_dock.show()

        for path in results:
            item = QListWidgetItem(path)
            item.setData(Qt.UserRole, path)
            self.search_results_list.addItem(item)

    def _on_search_result_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.UserRole)

        if not path or not os.path.exists(path):
            return

        # If it's a file, navigate to its parent directory for the active tab
        ctrl = self.get_active_controller()
        if not ctrl:
            return

        if os.path.isfile(path):
            parent_path = os.path.dirname(path)
            ctrl.set_current_path(parent_path)
        else:
            ctrl.set_current_path(path)

    # -------- Favorites menu update (toolbar owned) --------

    def update_favorites_menu(self):
        """
        Refresh the navigation toolbar favorites menu (used after changes).
        """
        if hasattr(self.toolbar, "update_favorites_menu"):
            self.toolbar.update_favorites_menu()
