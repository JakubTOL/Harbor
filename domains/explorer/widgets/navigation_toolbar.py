import os
from PySide6.QtWidgets import QToolBar, QPushButton, QMenu, QToolButton, QWidget, QSizePolicy
from PySide6.QtGui import QAction
from domains.explorer.widgets.search_widget import SearchWidget


class NavigationToolbar(QToolBar):

    def __init__(self, window, controller, favorites_manager):
        """
        Initialize the navigation toolbar with navigation actions and favorites menu.

        Args:
            window: The parent main window.
            controller: The ExplorerController for navigation logic.
            favorites_manager: The FavoritesManager instance for favorites operations.
        """
        super().__init__("Navigation")

        self.controller = controller
        self.favorites_manager = favorites_manager

        # -----------------------------
        # BASIC NAVIGATION
        # -----------------------------

        up = QAction("Up", window)
        home = QAction("Home", window)
        refresh = QAction("Refresh", window)

        up.triggered.connect(controller.go_up)
        home.triggered.connect(controller.go_home)
        refresh.triggered.connect(controller.refresh)

        self.addAction(up)
        self.addAction(home)
        self.addAction(refresh)

        # Add separator
        self.addSeparator()

        # -----------------------------
        # FAVORITES MENU
        # -----------------------------

        self.favorites_menu = QMenu("Favorites", self)
        self.favorites_button = QToolButton(self)
        self.favorites_button.setText("Favorites")
        self.favorites_button.setMenu(self.favorites_menu)
        self.favorites_button.setPopupMode(QToolButton.InstantPopup)
        self.addWidget(self.favorites_button)

        self.update_favorites_menu()

        # Add separator
        self.addSeparator()

        # -----------------------------
        # VIEW MODE SWITCH
        # -----------------------------

        self.addWidget(QPushButton("Tree", clicked=lambda: window.set_mode(0)))
        self.addWidget(QPushButton("Finder", clicked=lambda: window.set_mode(1)))

        # Add spacer to push search box to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)

        # Add separator
        self.addSeparator()

        # -----------------------------
        # SEARCH BOX
        # -----------------------------

        self.search_widget = SearchWidget(self)
        self.search_widget.search_triggered.connect(controller.perform_search)
        self.addWidget(self.search_widget)

    def update_favorites_menu(self):
        """
        Populate or refresh the favorites menu with current favorites.
        """
        self.favorites_menu.clear()
        for path in self.favorites_manager.all():
            dir_name = os.path.basename(path) or path  # root or base
            action = QAction(dir_name, self)
            # Set full path as tooltip, show full path on hover
            action.setToolTip(path)
            action.triggered.connect(lambda checked=False, p=path: self.controller.set_current_path(p))
            self.favorites_menu.addAction(action)