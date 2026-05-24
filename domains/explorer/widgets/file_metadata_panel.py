from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
import os
import time

class FileMetadataPanel(QWidget):
    def __init__(self, parent=None, max_height=48):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 2, 10, 2)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.label = QLabel("--", self)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.label)
        # Visual compactness
        self.setMaximumHeight(max_height)
        self.setMinimumHeight(32)
        # Subtle background and rounded corners for modern look
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f7;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #444;
                font-size: 11px;
            }
        """)

    def set_path(self, path):
        if not os.path.exists(path):
            self.label.setText("--")
            return
        stat = os.stat(path)
        size = stat.st_size
        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
        # Show GB/MB/KB for larger files, else bytes
        def human_size(sz):
            for unit in ['B','KB','MB','GB','TB']:
                if sz < 1024:
                    return f"{sz:.0f} {unit}"
                sz /= 1024
            return f"{sz:.0f} PB"
        info = f"""<b>Size:</b> {human_size(size)} &nbsp;&nbsp; <b>Modified:</b> {mtime}"""
        self.label.setText(info)