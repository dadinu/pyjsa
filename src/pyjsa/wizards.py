from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from pyjsa.assets.ui.Ui_newSetupWizard import Ui_NewSetupWizard
from pyjsa.profiles import SetupProfile


class NewSetupWizard(QtWidgets.QWizard, Ui_NewSetupWizard):
    finishedSetup = pyqtSignal(SetupProfile)
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setupProfile = SetupProfile()
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.onFinish)
        self.button(QtWidgets.QWizard.NextButton).clicked.connect(self.onNext)
        
    def onFinish(self):
        self.polingForm.loadToProfile(self.setupProfile)
        print(self.setupProfile.isRegularPoling())
        self.finishedSetup.emit(self.setupProfile)
        
    def onNext(self):
        if self.currentId() == 1:
            self.setupProfile.name = self.lineEditExperimentName.text()
            print(self.currentId())
        if self.currentId() == 2:
            self.processForm.loadToProfile(self.setupProfile)
            print(self.setupProfile.signalPol)
        if self.currentId() == 3:
            self.dispersionForm.loadToProfile(self.setupProfile)
            self.polingForm.setPolingFromProfile(self.setupProfile)
            print(self.currentId())
