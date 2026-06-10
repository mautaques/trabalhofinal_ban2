from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerência de Farmácia")
        self.showMaximized()
