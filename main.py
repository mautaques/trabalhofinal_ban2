from PyQt6.QtCore import Qt

import sys
import os

from PyQt6.QtWidgets import QApplication

cur_path = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(1, base_path)

app = QApplication([])
app.setApplicationName("Funcion Block Enviornment")

from mainWindow import MainWindow

window = MainWindow()
window.show()

app.exec()