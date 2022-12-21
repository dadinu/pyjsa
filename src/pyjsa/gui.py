import sys
from pyjsa._main_window import MainWindow
from PyQt5.QtWidgets import QApplication

def start_gui():
    app  = QApplication(sys.argv)
    gui = MainWindow()
    gui.setupUi(gui)
    gui.showMaximized()
    sys.exit(app.exec_())

