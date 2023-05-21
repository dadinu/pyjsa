from pyjsa.widgets import ProcessFormWidget, DispersionFormWidget
from pyjsa.wizards import NewSetupWizard
from pyjsa.windows import MainWindow
from PyQt5.QtWidgets import QWidget, QApplication

app = QApplication([])
#widget = DatabaseSelectorWidget("process")
widget = MainWindow()
widget.show()
app.exec_()