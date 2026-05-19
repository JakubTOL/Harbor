import sys
import os
from PySide6.QtWidgets import QApplication
from domains.explorer.views.explorer_window import ExplorerWindow
from PySide6.QtGui import QIcon


def resource_path(relative_path):
    # For PyInstaller compatibility
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def main():
    app = QApplication(sys.argv)

    # Set the app icon to show up in the taskbar and window - on Windows
    icon_path = resource_path('resources/icons/harbor.ico')
    app.setWindowIcon(QIcon(icon_path))

    window = ExplorerWindow()
    window.setWindowIcon(QIcon(icon_path))  # Explicitly set the window icon (optional but safe)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
