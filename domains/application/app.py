from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from domains.explorer.views.explorer_window import ExplorerWindow
from core.constants import ICON_PATH, SPLASH_PATH, SPLASH_SCREEN_WIDTH, SPLASH_SCREEN_HEIGHT
import sys
import os


def resource_path(relative_path):
    """
    Get the absolute path to a resource, resolving for PyInstaller if necessary.

    Args:
        relative_path (string): The relative path to the resource,

    Returns:
        str: The absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def prepare_splash(size_x: int, size_y: int):
    """
    Prepare and return a splash screen instance.

    Args:
        size_x (int): The width of the splash screen.
        size_y (int): The height of the splash screen.

    Returns:
        QSplashScreen: The configured splash screen object.
    """
    splash_image = QPixmap(resource_path(SPLASH_PATH)).scaled(size_x, size_y, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(splash_image)
    return splash


class HarborApplication:
    """
    Main application controller for the Harbor GUI app.

    This class is responsible for initializing and managing the Qt application lifecycle including:
        - Creating the QApplication instance
        - Displaying and closing the splash screen
        - Loading and applying the application icon
        - Creating and showing the main application window
        - Starting the Qt event loop
    """
    def __init__(self, argv=None):
        """
        Initialize the Harbor application instance.

        Creates the QApplication object and initializes internal references for the splash screen and main window.
        """
        self.argv = argv or sys.argv
        self.app = QApplication(self.argv)
        self.splash = None
        self.window = None

    def setup_splash(self):
        """
        Create and display the application splash screen.

        The splash screen is shown immediately while the main application window is being initialized.
        Qt events are processed to ensure the splash screen renders correctly.
        """
        self.splash = prepare_splash(SPLASH_SCREEN_WIDTH, SPLASH_SCREEN_HEIGHT)
        self.splash.show()
        self.app.processEvents()

    def setup_icon(self):
        """
        Load and apply the application window icon.

        Returns:
            QIcon: The loaded application icon instance.
        """
        icon = QIcon(resource_path(ICON_PATH))
        self.app.setWindowIcon(icon)
        return icon

    def run(self):
        """
        Start and execute the application.

        This method performs the full startup sequence:
        1. Display the splash screen.
        2. Loads the application icon.
        3. Creates the main ExplorerWindow.
        4. Shows the main window.
        5. Closes the splash screen.
        6. Starts the Qt event loop.

        Raises:
            SystemExit: If the application was not started successfully or event loop exits.
        """
        self.setup_splash()
        icon = self.setup_icon()
        self.window = ExplorerWindow()
        self.window.setWindowIcon(icon)
        self.window.show()
        self.splash.finish(self.window)
        sys.exit(self.app.exec())
