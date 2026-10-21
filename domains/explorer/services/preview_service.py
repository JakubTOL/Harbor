# domains/explorer/services/preview_service.py

from pathlib import Path
from typing import Dict, Optional
from domains.explorer.widgets.preview_window import PreviewWindow


class PreviewService:
    """
    Keeps preview windows managed and prevents duplicates.
    """

    def __init__(self):
        self._windows: Dict[str, PreviewWindow] = {}

    def show_preview(self, file_path: str, parent=None) -> Optional[PreviewWindow]:
        normalized = str(Path(file_path).resolve())

        if normalized in self._windows:
            window = self._windows[normalized]
            if window.isVisible():
                window.raise_()
                window.activateWindow()
                return window
            del self._windows[normalized]

        preview = PreviewWindow(normalized, parent)
        preview.show()
        self._windows[normalized] = preview

        preview.destroyed.connect(
            lambda: self._windows.pop(normalized, None)
        )
        return preview

    def close_all(self):
        for w in list(self._windows.values()):
            if w.isVisible():
                w.close()
        self._windows.clear()