from PySide6.QtWidgets import QTreeView


class ExplorerTree(QTreeView):

    def __init__(self, model, on_click):
        super().__init__()

        self.setModel(model)
        self.setColumnWidth(0, 300)

        for i in range(1, 4):
            self.hideColumn(i)

        self.clicked.connect(on_click)