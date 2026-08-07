from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QTimer, Signal, QMargins


class SearchWidget(QLineEdit):
    """
    Search input box for the navigation toolbar.
    Emits search signal with debouncing to avoid excessive searches.
    """

    search_triggered = Signal(str)  # Emits search query

    def __init__(self, parent=None):
        """
        Initialize the search widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setPlaceholderText("Search files...")
        self.setMaximumWidth(200)

        # Add right margin to create spacing from window border
        self.setContentsMargins(0, 0, 10, 0)

        # Debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._on_timer_timeout)

        # Connect text changes with debouncing
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str) -> None:
        """
        Handle text change with debouncing.
        Waits 300ms before emitting search signal.

        Args:
            text: Current text in the input field
        """
        # Restart debounce timer
        self.search_timer.stop()
        self.search_timer.start(100)  # 100ms delay

    def _on_timer_timeout(self) -> None:
        """
        Called when debounce timer expires.
        Emits the search signal with current text.
        """
        self.search_triggered.emit(self.text())