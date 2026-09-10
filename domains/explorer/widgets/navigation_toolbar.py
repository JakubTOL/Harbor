# domains/explorer/widgets/navigation_toolbar.py
import os
from pathlib import Path
from PySide6.QtWidgets import QToolBar, QPushButton, QMenu, QToolButton, QWidget, QSizePolicy
from PySide6.QtGui import QAction
from domains.explorer.widgets.search_widget import SearchWidget


class NavigationToolbar(QToolBar):

    def __init__(self, window, favorites_manager):
        super().__init__("Navigation")

        self.window = window
        self.favorites_manager = favorites_manager

        # Basic navigation actions use controller (via window.get_active_controller)
        up = QAction("Up", window)
        home = QAction("Home", window)
        refresh = QAction("Refresh", window)

        up.triggered.connect(lambda: self._call_active("go_up"))
        home.triggered.connect(lambda: self._call_active("go_home"))
        refresh.triggered.connect(lambda: self._call_active("refresh"))

        self.addAction(up)
        self.addAction(home)
        self.addAction(refresh)

        self.addSeparator()

        # Tab actions
        new_tab_act = QAction("New Tab", window)
        close_tab_act = QAction("Close Tab", window)
        new_tab_act.triggered.connect(lambda: window.create_new_tab())
        close_tab_act.triggered.connect(lambda: window.close_current_tab())

        self.addAction(new_tab_act)
        self.addAction(close_tab_act)

        self.addSeparator()

        # Favorites menu
        self.favorites_menu = QMenu("Favorites", self)
        self.favorites_button = QToolButton(self)
        self.favorites_button.setText("Favorites")
        self.favorites_button.setMenu(self.favorites_menu)
        self.favorites_button.setPopupMode(QToolButton.InstantPopup)
        self.addWidget(self.favorites_button)
        self.update_favorites_menu()

        self.addSeparator()

        # VIEW MODE SWITCH - call the active TAB (view) set_mode, not controller
        self.addWidget(QPushButton("Tree", clicked=lambda: self._call_active_tab("set_mode", 0)))
        self.addWidget(QPushButton("Finder", clicked=lambda: self._call_active_tab("set_mode", 1)))

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)

        self.addSeparator()

        # Search box delegates to window.perform_search which routes to active controller
        self.search_widget = SearchWidget(self)
        self.search_widget.search_triggered.connect(window.perform_search)
        self.addWidget(self.search_widget)

    def _call_active(self, method_name: str, *args, **kwargs):
        ctrl = self.window.get_active_controller()
        if not ctrl:
            return
        method = getattr(ctrl, method_name, None)
        if method:
            return method(*args, **kwargs)

    def _call_active_tab(self, method_name: str, *args, **kwargs):
        """
        Call a method on the active tab (the view), e.g., set_mode.
        """
        tab = self.window.get_active_tab()
        if not tab:
            return
        method = getattr(tab, method_name, None)
        if method:
            return method(*args, **kwargs)

    def update_favorites_menu(self):
        self.favorites_menu.clear()
        for path in self.favorites_manager.all():
            dir_name = os.path.basename(path) or path
            action = QAction(dir_name, self)
            action.setToolTip(path)
            action.triggered.connect(lambda checked=False, p=path: self._on_favorite_selected(p))
            self.favorites_menu.addAction(action)

    def _on_favorite_selected(self, path: str):
        ctrl = self.window.get_active_controller()
        if ctrl:
            ctrl.set_current_path(path)
