from PySide6.QtWidgets import QTreeView, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QPoint, Qt

class ExplorerTree(QTreeView):

    def __init__(self, model, on_double_click, controller=None):
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

    def expand_or_collapse_on_click(self, index):
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)

    def show_context_menu(self, point: QPoint):
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
