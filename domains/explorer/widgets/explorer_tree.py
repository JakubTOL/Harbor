from PySide6.QtWidgets import QTreeView


class ExplorerTree(QTreeView):

    def __init__(self, model, on_click):
        super().__init__()

        self.setModel(model)
        self.setColumnWidth(0, 300)

        for i in range(1, 4):
            self.hideColumn(i)

        self.clicked.connect(on_click)
        self.clicked.connect(self.expand_or_collapse_on_click)

    def expand_or_collapse_on_click(self, index):
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)
