# domains/explorer/widgets/preview_window.py

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QScrollArea,
    QMessageBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QImage
import os

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None


class PreviewWindow(QMainWindow):
    """
    Floating Quick Look style preview window.
    Supports:
      - .txt, .csv, .tsv, .py, .json, .xml, .md, .html, .yaml, .yml, .ini, .toml, .log
      - .pdf
      - .jpg, .jpeg, .png, .gif, .bmp, .webp
    """

    TEXT_EXTENSIONS = {
        ".txt", ".csv", ".tsv", ".py", ".json", ".xml", ".md",
        ".html", ".yaml", ".yml", ".ini", ".toml", ".log",
        ".js", ".ts", ".css", ".sql", ".java", ".sh"
    }
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    PDF_EXTENSIONS = {".pdf"}

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Preview: {os.path.basename(file_path)}")
        self.resize(900, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self._build_ui()
        self._load_preview()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        self.info_label = QLabel(os.path.basename(self.file_path))
        self.info_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(self.info_label)
        header_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedWidth(90)
        header_layout.addWidget(close_btn)

        header.setStyleSheet("border-bottom: 1px solid #d0d0d0; background: #f7f7f7;")
        root_layout.addWidget(header)

        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.content_container)

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            self.close()
        super().keyPressEvent(event)

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _show_error(self, message: str):
        self._clear_content()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("color: #666; font-size: 13px; padding: 20px;")
        self.content_layout.addWidget(label)

    def _load_preview(self):
        path = Path(self.file_path)

        if not path.exists():
            self._show_error("File not found.")
            return

        if path.is_dir():
            self._show_error("This is a folder, not a file.")
            return

        file_size = path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50 MB
            self._show_error("File is too large to preview.")
            return

        suffix = path.suffix.lower()

        if suffix in self.TEXT_EXTENSIONS:
            self._render_text(path)
        elif suffix in self.IMAGE_EXTENSIONS:
            self._render_image(path)
        elif suffix in self.PDF_EXTENSIONS:
            self._render_pdf(path)
        else:
            self._show_error(
                f"Preview is not supported for '{suffix}'\n\n"
                "Open it in the default application instead."
            )

    def _render_text(self, path: Path):
        try:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="latin-1")

            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Courier", 10))
            text_edit.setPlainText(content)

            self._clear_content()
            self.content_layout.addWidget(text_edit)
            self.info_label.setText(f"📄 {path.name}")
        except Exception as exc:
            self._show_error(f"Failed to read text file:\n{exc}")

    def _render_image(self, path: Path):
        try:
            pixmap = QPixmap(str(path))
            if pixmap.isNull():
                self._show_error("Image could not be loaded.")
                return

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setPixmap(pixmap)
            scroll.setWidget(label)

            self._clear_content()
            self.content_layout.addWidget(scroll)
            self.info_label.setText(f"🖼️ {path.name}")
        except Exception as exc:
            self._show_error(f"Failed to load image:\n{exc}")

    def _render_pdf(self, path: Path):
        if fitz is None:
            self._show_error(
                "PDF preview requires PyMuPDF.\n\n"
                "Install it with: pip install PyMuPDF"
            )
            return

        try:
            doc = fitz.open(str(path))

            if doc.page_count == 0:
                self._show_error("PDF is empty.")
                return

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)
            page_layout.setContentsMargins(12, 12, 12, 12)

            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                qimage = self._convert_pixmap_to_qimage(pix)

                label = QLabel()
                label.setPixmap(QPixmap.fromImage(qimage))
                label.setAlignment(Qt.AlignCenter)
                page_layout.addWidget(label)

            page_widget.setLayout(page_layout)
            scroll.setWidget(page_widget)

            self._clear_content()
            self.content_layout.addWidget(scroll)
            self.info_label.setText(f"📕 {path.name} | {doc.page_count} pages")

        except Exception as exc:
            self._show_error(f"Failed to render PDF:\n{exc}")

    def _convert_pixmap_to_qimage(self, pixmap):
        samples = pixmap.samples
        width = pixmap.width
        height = pixmap.height
        n = pixmap.n

        if n == 4:
            fmt = QImage.Format_RGBA8888
        else:
            fmt = QImage.Format_RGB888

        image = QImage(samples, width, height, n * width, fmt)
        return image