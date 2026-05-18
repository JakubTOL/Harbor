import sys
from PySide6.QtWidgets import QApplication
from domains.explorer.views.explorer_window import ExplorerWindow


def main():
    app = QApplication(sys.argv)

    window = ExplorerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()