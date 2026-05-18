from PySide6.QtWidgets import QToolBar, QPushButton
from PySide6.QtGui import QAction


class NavigationToolbar(QToolBar):

    def __init__(self, window, controller):

        super().__init__("Navigation")

        self.controller = controller

        up = QAction("Up", window)
        home = QAction("Home", window)
        refresh = QAction("Refresh", window)

        up.triggered.connect(controller.go_up)
        home.triggered.connect(controller.go_home)
        refresh.triggered.connect(controller.refresh)

        self.addAction(up)
        self.addAction(home)
        self.addAction(refresh)

        self.addWidget(QPushButton("Tree", clicked=lambda: window.set_mode(0)))
        self.addWidget(QPushButton("Finder", clicked=lambda: window.set_mode(1)))