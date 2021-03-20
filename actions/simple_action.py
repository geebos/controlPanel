from PyQt5.Qt import *


class SimpleAction(QAction):
    def __init__(self, parent, icon, text, callback):
        super(SimpleAction, self).__init__(parent=parent)
        self.setIcon(QIcon(icon))
        self.setText(text)
        self.triggered.connect(callback)
