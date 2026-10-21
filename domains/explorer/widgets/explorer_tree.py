from PySide6.QtWidgets import QTreeView, QMenu
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtCore import QPoint, Qt, QEvent

class ExplorerTree(QTreeView):

    def __init__(self, model, on_double_click, controller=None):
        """
        Initialize the tree view for the file explorer.

        Args:
            model: The QFileSystemModel for displaying filesystem.
            on_double_click: Callback for double-click events.
            controller: The ExplorerController for the context menu actions.
        """
        super().__init__()
        self.setModel(model)
        self.setColumnWidth(0, 300)
        self.controller = controller

        for i in range(1, 4):
            self.hideColumn(i)

        self.doubleClicked.connect(on_double_click)
        self.clicked.connect(self.expand_or_collapse_on_click)

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # focus matters
        self.setFocusPolicy(Qt.StrongFocus)
        self.viewport().setFocusPolicy(Qt.StrongFocus)

        # install on viewport, not only on the outer view
        self.viewport().installEventFilter(self)

        def eventFilter(self, obj, event):
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
                if self.controller is not None:
                    self.controller.show_preview_for_current_selection()
                return True
            return super().eventFilter(obj, event)

    def expand_or_collapse_on_click(self, index):
        """
        Expand or collapse a tree node upon click.

        Args:
            index: The QModelIndex of the clicked node.
        """
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Space:
                print("SPACE pressed on tree view")

                idx = self.currentIndex()
                if idx.isValid():
                    path = self.model().filePath(idx)
                    print("current path:", path)

                    if self.controller is not None:
                        if not self.model().isDir(idx):
                            # do not rely on selectedIndexes
                            self.controller.show_preview_for_current_selection()
                            return True

                return True  # consume the key, even if no preview

        return super().eventFilter(obj, event)

    def show_context_menu(self, point: QPoint):
        """
        Show context menu at given point.

        Args:
            point (QPoint): The location to show context menu at.
        """
        index = self.indexAt(point)
        if index.isValid():  # Right-clicked on file/folder
            self.controller.show_context_menu(self, index, point, directory_mode=False)
        else:  # Right-clicked empty area: use folder this column is displaying
            dir_index = self.rootIndex()  # This index points to the folder backing the column/list/tree
            self.controller.show_context_menu(self, dir_index, point, directory_mode=True)

        menu = QMenu(self)

        rename_action = QAction("Rename", self)
        new_file_action = QAction("New File", self)
        new_folder_action = QAction("New Folder", self)
        delete_action = QAction("Delete", self)

        # Connect actions
        rename_action.triggered.connect(lambda: self.controller.rename_item(index))
        new_file_action.triggered.connect(lambda: self.controller.create_new_file(index))
        new_folder_action.triggered.connect(lambda: self.controller.create_new_folder(index))
        delete_action.triggered.connect(lambda: self.controller.delete_item(index))

        menu.addAction(rename_action)
        menu.addAction(new_file_action)
        menu.addAction(new_folder_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec(self.viewport().mapToGlobal(point))

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

        if self.controller.fs is None:
            return

        selected = self.selectedIndexes()
        if not selected:
            return

        index = selected[0]
        path = self.controller.fs.file_path(index)

        if self.controller.fs.is_dir(path):
            return

        self.controller.show_preview_for_current_selection()