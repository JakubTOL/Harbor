import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QLabel


class BreadcrumbBar(QWidget):

    def __init__(self, on_navigate):
        super().__init__()

        self.on_navigate = on_navigate

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)

        self.current_path = ""

    def set_path(self, path: str):
        self.current_path = path
        self._render()

    def _clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render(self):

        self._clear()

        path = Path(self.current_path)
        parts = list(path.parts)

        cumulative = ""

        for i, part in enumerate(parts):

            if i == 0:
                cumulative = part
            else:
                cumulative = os.path.join(cumulative, part)

            btn = QToolButton()
            btn.setText(part if part else "/")

            btn.clicked.connect(
                lambda _, p=cumulative: self.on_navigate(p)
            )

            self.layout.addWidget(btn)

            if i < len(parts) - 1:
                self.layout.addWidget(QLabel(">"))

        self.layout.addStretch()