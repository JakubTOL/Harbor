import sys
import os
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

from domains.explorer.views.explorer_window import ExplorerWindow


def resource_path(relative_path):
    # For PyInstaller compatibility
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def prepare_splash(size_x, size_y):
    _splash_image = QPixmap('resources/harbor.png').scaled(size_x, size_y, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    _splash = QSplashScreen(_splash_image)
    return _splash


def main():
    app = QApplication(sys.argv)

    #TODO: Finish splash screen feature
    from time import sleep

    splash = prepare_splash(size_x=450, size_y=450)
    splash.show()
    sleep(3)
    # Set the app icon to show up in the taskbar and window - on Windows
    icon_path = resource_path('resources/icons/harbor.ico')
    app.setWindowIcon(QIcon(icon_path))

    window = ExplorerWindow()
    window.setWindowIcon(QIcon(icon_path))  # Explicitly set the window icon (optional but safe)
    window.show()
    splash.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
