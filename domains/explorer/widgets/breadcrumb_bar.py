import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QLabel
from core.constants import BREADCRUMB_RENDER_LIMIT


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

        max_visible = BREADCRUMB_RENDER_LIMIT
        n_parts = len(parts)

        # Decide which parts to display
        if n_parts > max_visible:
            show_parts = parts[-max_visible:]
            truncated = True
        else:
            show_parts = parts
            truncated = False

        cumulative = ""
        # "..." button for truncated breadcrumbs
        if truncated:
            btn = QToolButton()
            btn.setText("...")
            # Optional: Navigate to root or open a dropdown
            btn.clicked.connect(lambda: self.on_navigate(str(Path(*parts[:1]))))
            self.layout.addWidget(btn)
            self.layout.addWidget(QLabel(">"))

        for i, part in enumerate(show_parts):
            if truncated:
                idx = n_parts - max_visible + i
            else:
                idx = i

            # Rebuild cumulative path up to this part
            if idx == 0:
                cumulative = parts[0]
            else:
                cumulative = os.path.join(*parts[: idx + 1])

            btn = QToolButton()
            btn.setText(part if part else "/")
            btn.clicked.connect(lambda _, p=cumulative: self.on_navigate(p))
            self.layout.addWidget(btn)

            if i < len(show_parts) - 1:
                self.layout.addWidget(QLabel(">"))

        self.layout.addStretch()
