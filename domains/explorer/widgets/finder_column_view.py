from PySide6.QtWidgets import QColumnView


class FinderColumnView(QColumnView):

    def __init__(self, model, on_click, on_double_click):
        super().__init__()

        self.setModel(model)
        # self.clicked.connect(on_click)
        self.doubleClicked.connect(on_double_click)
