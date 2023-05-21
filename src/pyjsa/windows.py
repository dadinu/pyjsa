import pyqtgraph as pqg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QWizard, QMdiSubWindow, QMdiArea
from pyjsa.assets.ui.Ui_mainWindow import Ui_MainWindow

from pyjsa.wizards import NewSetupWizard
from pyjsa.profiles import SetupProfile
from pyjsa.widgets import ProcessFormWidget, DispersionFormWidget, PolingFormWidget
from pyjsa.simulation import SPDC

import numpy as np

def getSubWindowTitles(mdiArea: QMdiArea):
    result = []
    for window in mdiArea.subWindowList():
        result.append(window.windowTitle())
    return result

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        newSetupWizard = NewSetupWizard(self)
        newSetupWizard.open()
        newSetupWizard.finishedSetup.connect(self.setSetup)
        
        self.actionNewSetup.triggered.connect(newSetupWizard.open)
        self.actionClose.triggered.connect(self.closeSetup)
        self.actionProcessForm.triggered.connect(self.openProcessForm)
        self.actionDispersionForm.triggered.connect(self.openDispersionForm)
        self.actionPolingForm.triggered.connect(self.openPolingForm)
        self.actionRun.triggered.connect(self.runSetup)
        self.actionPEF.triggered.connect(self.openPEF)
        self.actionPMF.triggered.connect(self.openPMF)
        self.actionJSA.triggered.connect(self.openJSA)
        
    def openProcessForm(self):
        self.processForm = ProcessFormWidget()
        self.processFormMdiWindow = QMdiSubWindow()
        self.processFormMdiWindow.setWidget(self.processForm)
        self.processFormMdiWindow.setWindowTitle("Process Form")
        self.mdiArea.addSubWindow(self.processFormMdiWindow)
        
        self.processForm.loadFromProfile(self.setup)
        self.processForm.dataChanged.connect(lambda: self.processForm.loadToProfile(self.setup))
        self.processForm.dataChanged.connect(self._changePolingPeriod)
        self.processFormMdiWindow.show()
        
    def openDispersionForm(self):
        self.dispersionForm = DispersionFormWidget()
        self.dispersionFormMdiWindow = QMdiSubWindow()
        self.dispersionFormMdiWindow.setWidget(self.dispersionForm)
        self.dispersionFormMdiWindow.setWindowTitle("Dispersion Form")
        self.mdiArea.addSubWindow(self.dispersionFormMdiWindow)
        
        self.dispersionForm.loadFromProfile(self.setup)
        self.dispersionForm.dataChanged.connect(lambda: self.dispersionForm.loadToProfile(self.setup))
        self.dispersionForm.dataChanged.connect(self._changePolingPeriod)
        
        self.dispersionFormMdiWindow.show()
        
    def openPolingForm(self):
        self.polingForm = PolingFormWidget()
        self.polingFormMdiWindow = QMdiSubWindow()
        self.polingFormMdiWindow.setWidget(self.polingForm)
        self.polingFormMdiWindow.setWindowTitle("Poling Form")
        self.mdiArea.addSubWindow(self.polingFormMdiWindow)
        
        self.polingForm.loadFromProfile(self.setup)
        self.polingForm.setPolingFromProfile(self.setup)
        self.polingForm.dataChanged.connect(lambda: self.polingForm.loadToProfile(self.setup))
        self.polingFormMdiWindow.show()
        
    def openPEF(self):
        self.PEFMdiWindow = QMdiSubWindow()
        self.PEFPlot = pqg.PlotWidget()
        self.PEFPlot.addItem(pqg.ImageItem(np.abs(self.SPDC.pef), colorMap = 'inferno'))
        self.PEFMdiWindow.setWidget(self.PEFPlot)
        self.PEFMdiWindow.setWindowTitle("Pump envelope function")
        self.mdiArea.addSubWindow(self.PEFMdiWindow)
        
        self.PEFMdiWindow.show()
        
    def openPMF(self):
        self.PMFMdiWindow = QMdiSubWindow()
        self.PMFPlot = pqg.PlotWidget()
        self.PMFPlot.addItem(pqg.ImageItem(np.abs(self.SPDC.pmf), colorMap = 'inferno'))
        self.PMFMdiWindow.setWidget(self.PMFPlot)
        self.PMFMdiWindow.setWindowTitle("Phase-matching function")
        self.mdiArea.addSubWindow(self.PMFMdiWindow)
        
        self.PMFMdiWindow.show()
        
    def openJSA(self):
        self.JSAMdiWindow = QMdiSubWindow()
        self.JSAPlot = pqg.PlotWidget()
        self.JSAPlot.addItem(pqg.ImageItem(np.abs(self.SPDC.jsa), colorMap = 'inferno'))
        self.JSAPlot.addItem(pqg.TextItem(f"Purity: {self.SPDC.purity}%"))
        self.JSAMdiWindow.setWidget(self.JSAPlot)
        self.JSAMdiWindow.setWindowTitle("Joint Spectral Amplitude")
        self.mdiArea.addSubWindow(self.JSAMdiWindow)
        
        self.JSAMdiWindow.show()
        
        
    def setSetup(self, value: SetupProfile):
        self.setup = value
        self.actionClose.setEnabled(True)
        self.actionSaveSetup.setEnabled(True)
        self.actionRenameSetup.setEnabled(True)
        self.actionProcessForm.setEnabled(True)
        self.actionDispersionForm.setEnabled(True)
        self.actionPolingForm.setEnabled(True)
        self.actionRun.setEnabled(True)
        self.actionPEF.setEnabled(True)
        self.actionPMF.setEnabled(True)
        self.actionJSA.setEnabled(True)
        
        self.SPDC = SPDC(self.setup, [200, 200])
        self.SPDC.PEF()
        self.SPDC.PMF()
        self.SPDC.JSA()
        
        self.openPEF()
        self.openPMF()
        self.openJSA()
        
    def runSetup(self):
        self.SPDC = SPDC(self.setup, [200, 200])
        self.SPDC.PEF()
        self.SPDC.PMF()
        self.SPDC.JSA()
        
        if self.PEFMdiWindow in self.mdiArea.subWindowList():
            self.PEFPlot.clear()
            self.PEFPlot.addItem(pqg.ImageItem(np.abs(self.SPDC.pef), colorMap = 'inferno'))
        if self.PMFMdiWindow in self.mdiArea.subWindowList():
            self.PMFPlot.clear()
            self.PMFPlot.addItem(pqg.ImageItem(np.abs(self.SPDC.pmf), colorMap = 'inferno'))
        if self.JSAMdiWindow in self.mdiArea.subWindowList():
            self.JSAPlot.clear()
            self.JSAPlot.addItem(pqg.ImageItem(np.abs(self.SPDC.jsa), colorMap = 'inferno'))
            self.JSAPlot.addItem(pqg.TextItem(f"Purity: {self.SPDC.purity}%"))
            
        
    def closeSetup(self):
        self.mdiArea.closeAllSubWindows()
    
    def _changePolingPeriod(self):
        if hasattr(self, 'polingForm'):
            self.polingForm.setPolingFromProfile(self.setup)