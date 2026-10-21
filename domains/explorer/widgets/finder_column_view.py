from PySide6.QtWidgets import QColumnView
from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QShortcut, QKeySequence

class FinderColumnView(QColumnView):

    def __init__(self, model, on_click, on_double_click, controller=None):
        """
        Initialize the Finder-style column view.

        Args:
            model: The QFileSystem for the view.
            on_click: Callback for click events (optional).
            on_double_clikc: Callback for double-click events.
            controller: The ExplorerController for context menus.
        """
        super().__init__()
        self.setModel(model)
        # self.clicked.connect(on_click)
        self.doubleClicked.connect(on_double_click)
        self.controller = controller
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setFocusPolicy(Qt.StrongFocus)
        self.viewport().setFocusPolicy(Qt.StrongFocus)
        self.viewport().installEventFilter(self)

    def show_context_menu(self, point: QPoint):
        index = self.indexAt(point)
        if index.isValid():  # Right-clicked on file/folder
            self.controller.show_context_menu(self, index, point, directory_mode=False)
        else:  # Right-clicked empty area: use folder this column is displaying
            dir_index = self.rootIndex()
            self.controller.show_context_menu(self, dir_index, point, directory_mode=True)
        # removed the extra self.controller.show_context_menu(...) call

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.controller is not None:
                self.controller.show_preview_for_current_selection()
            event.accept()
            return

        super().keyPressEvent(event)

    def _on_space_pressed(self):
        if self.controller is None:
            return

        selected = self.selectedIndexes()
        if not selected:
            return

        index = selected[0]
        path = self.controller.fs.file_path(index)

        if self.controller.fs.is_dir(path):
            return

        self.controller.show_preview_for_current_selection()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Space:
                print("SPACE pressed on finder view")

                idx = self.currentIndex()
                if idx.isValid():
                    path = self.model().filePath(idx)
                    print("finder current path:", path)

                    if self.controller is not None:
                        if not self.model().isDir(idx):
                            self.controller.show_preview_for_current_selection()
                            return True

                return True

        return super().eventFilter(obj, event)