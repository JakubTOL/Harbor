from PySide6.QtWidgets import QTreeView
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.controller is not None:
                self.controller.show_preview_for_current_selection()
            event.accept()
            return

        super().keyPressEvent(event)
