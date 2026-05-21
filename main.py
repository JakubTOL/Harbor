import sys
import os
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

from domains.explorer.views.explorer_window import ExplorerWindow
from core.constants import ICON_PATH, SPLASH_PATH, SPLASH_SCREEN_WIDTH, SPLASH_SCREEN_HEIGHT


def resource_path(relative_path):
    """
    GEt the absolute path to a resource, resolving for PyInstaller if necessary.

    Args:
        relative_path (string): The relative path to the resource,

    Returns:
        str: The absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def prepare_splash(size_x, size_y):
    _splash_image = QPixmap(SPLASH_PATH).scaled(size_x, size_y, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    _splash = QSplashScreen(_splash_image)
    return _splash


def main():
    app = QApplication(sys.argv)

    #TODO: Finish splash screen feature
    from time import sleep

    splash = prepare_splash(size_x=SPLASH_SCREEN_WIDTH, size_y=SPLASH_SCREEN_HEIGHT)
    splash.show()
    sleep(3)
    # Set the app icon to show up in the taskbar and window - on Windows
    icon_path = resource_path(ICON_PATH)
    app.setWindowIcon(QIcon(icon_path))

    window = ExplorerWindow()
    window.setWindowIcon(QIcon(icon_path))  # Explicitly set the window icon (optional but safe)
    window.show()
    splash.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
