from PySide6.QtWidgets import QColumnView
from PySide6.QtCore import Qt, QPoint

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

    def show_context_menu(self, point: QPoint):
        """
        Show context menu at given point in the column view.

        Args:
            point (QPoint): The location for the menu.
        """
        index = self.indexAt(point)
        if index.isValid():  # Right-clicked on file/folder
            self.controller.show_context_menu(self, index, point, directory_mode=False)
        else:  # Right-clicked empty area: use folder this column is displaying
            dir_index = self.rootIndex()  # This index points to the folder backing the column/list/tree
            self.controller.show_context_menu(self, dir_index, point, directory_mode=True)
        self.controller.show_context_menu(self, index, point)
