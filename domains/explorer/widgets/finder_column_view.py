from PySide6.QtWidgets import QColumnView
from PySide6.QtCore import Qt, QPoint

class FinderColumnView(QColumnView):

    def __init__(self, model, on_click, on_double_click, controller=None):
        super().__init__()
        self.setModel(model)
        # self.clicked.connect(on_click)
        self.doubleClicked.connect(on_double_click)
        self.controller = controller
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, point: QPoint):
        index = self.indexAt(point)
        if not index.isValid() or not self.controller:
            return
        self.controller.show_context_menu(self, index, point)
