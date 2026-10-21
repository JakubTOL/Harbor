# domains/explorer/widgets/tab_bar.py
from PySide6.QtWidgets import QTabBar
from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen


class AddTabTabBar(QTabBar):
    plusClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._plus_rect = QRect()
        self._show_plus = False

    def mouseMoveEvent(self, event):
        self._update_plus_state(event.pos())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._show_plus = False
        self._plus_rect = QRect()
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._plus_rect.contains(event.pos()):
            self.plusClicked.emit()
            return
        super().mousePressEvent(event)

    def _update_plus_state(self, pos):
        if self.count() == 0:
            self._show_plus = False
            self._plus_rect = QRect()
            self.update()
            return

        # Only show the + when near the end of the last tab
        last_tab = self.tabRect(self.count() - 1)
        if not last_tab.isValid():
            self._show_plus = False
            self._plus_rect = QRect()
            self.update()
            return

        margin = 30
        near_end = pos.x() >= (self.width() - margin)

        if near_end and pos.y() >= 0 and pos.y() <= self.height():
            size = 18
            x = self.width() - size - 10
            y = (self.height() - size) // 2
            self._plus_rect = QRect(x, y, size, size)
            self._show_plus = True
        else:
            self._plus_rect = QRect()
            self._show_plus = False

        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self._show_plus or not self._plus_rect.isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor("#e8edf3"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self._plus_rect, 5, 5)

        painter.setPen(QPen(QColor("#2a2a2a"), 2))
        cx = self._plus_rect.center().x()
        cy = self._plus_rect.center().y()
        pad = 4
        painter.drawLine(cx, cy - pad, cx, cy + pad)
        painter.drawLine(cx - pad, cy, cx + pad, cy)