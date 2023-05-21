import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPaintEvent, QMouseEvent
from math import tan, radians
import numpy as np
import pyqtgraph as pqg

from PyQt5.QtWidgets import QWidget

from pyjsa.assets.ui.Ui_processForm import Ui_ProcessForm
from pyjsa.assets.ui.Ui_databaseSelector import Ui_DatabaseSelector
from pyjsa.assets.ui.Ui_dispersionForm import Ui_DispersionForm
from pyjsa.assets.ui.Ui_polingForm import Ui_PolingForm
from pyjsa.models import DatabaseListModel
from pyjsa.profiles import SetupProfile, DispersionProfile, PyJSATable, Profile
from pyjsa.utils import pmfGaussian, findGaussianProfile

#TODO: implement proper PyQt5 styleshhet
STYLESHEET = {
    'background-substrate': "#FF5E6472",
    'background-waveguide': "#FF42033D",
    'background-cladding': "#FFD6D9CE",
    'hover-cladding': '#80D6D9CE',
    'hover-waveguide': '#8042033D',
    'hover-substrate': '#805E6472'
}


class RidgeWaveguideWidget(QtWidgets.QWidget):
    
    #signals
    cladding_toggled = pyqtSignal()
    waveguide_toggled = pyqtSignal()
    substrate_toggled = pyqtSignal()
    
    def __init__(self, 
                 wg_width = 150, 
                 wg_height = 75, 
                 film_thickness = 150, 
                 substrate_thickness = 150, 
                 cladding_thickness = 150,
                 film_width = 450,
                 angle = 60,
                 *args, **kwargs):
        super(RidgeWaveguideWidget, self).__init__(*args, **kwargs)
        self._wg_width = wg_width
        self._wg_height = wg_height
        self._film_thickness = film_thickness
        self._substrate_thickness = substrate_thickness
        self._cladding_thickness = cladding_thickness
        self._film_width = film_width
        self._angle = angle
        
        self.r1 = self._film_thickness/self._cladding_thickness
        self.r2 = self._substrate_thickness/self._cladding_thickness
        self.r3 = self._wg_height/self._film_thickness
        self.r4 = self._wg_width/self._film_width
        
        self._constructPolys(self.width(), self.height())
        self._constructParts()
        
        
    @property
    def wg_width(self):
        return self._wg_width
    
    @wg_width.setter
    def wg_width(self, value):
        self._wg_width = value
        self.r4 = self._wg_width/self._film_width
        
    @property
    def wg_height(self):
        return self._wg_height
    
    @wg_height.setter
    def wg_height(self, value):
        self._wg_height = value
        self.r3 = self._wg_height/self._film_thickness
        
    @property
    def film_thickness(self):
        return self._film_thickness
    
    @film_thickness.setter
    def film_thickness(self, value):
        self._film_thickness = value
        self.r3 = self._wg_height/self._film_thickness
        self.r1 = self._film_thickness/self._cladding_thickness
        
    @property
    def substrate_thickness(self):
        return self._substrate_thickness
    
    @substrate_thickness.setter
    def substrate_thickenss(self, value):
        self._substrate_thickness = value
        self.r2 = self._substrate_thickness/self._cladding_thickness
        
    @property
    def cladding_thickness(self):
        return self._cladding_thickness
    
    @cladding_thickness.setter
    def cladding_thickness(self, value):
        self._substrate_thickness = value
        self.r1 = self._film_thickness/self._cladding_thickness
        self.r2 = self._substrate_thickness/self._cladding_thickness
        
    @property
    def film_width(self):
        return self._film_width
    
    @film_width.setter
    def film_width(self, value):
        self._film_width = value
        self.r4 = self._wg_width/self._film_width
    
    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
    
    def _constructPolys(self, W, H):
        film_width = W
        wg_width = self.r4*W
        cladding_thickness = H/(1+self.r1+self.r2)
        film_thickness = H*self.r1/(1+self.r1+self.r2)
        substrate_thickness = H*self.r2/(1+self.r1+self.r2)
        wg_height = self.r3*film_thickness
        
        self._cladding_poly = QtGui.QPolygonF()
        self._cladding_poly << QPoint(0,0) << QPoint(film_width,0) << QPoint(film_width, cladding_thickness+wg_height)\
            << QPoint((film_width+wg_width)/2,cladding_thickness+wg_height)\
            << QPoint((film_width+wg_width)/2-wg_height/tan(radians(self.angle)), cladding_thickness)\
            << QPoint((film_width-wg_width)/2+wg_height/tan(radians(self.angle)),cladding_thickness)\
            << QPoint((film_width-wg_width)/2,cladding_thickness+wg_height) << QPoint(0, cladding_thickness+wg_height)
        
    
        self._waveguide_poly = QtGui.QPolygonF()
        self._waveguide_poly << QPoint(film_width, cladding_thickness+wg_height)\
                             << QPoint((film_width+wg_width)/2,cladding_thickness+wg_height)\
                             << QPoint((film_width+wg_width)/2-wg_height/tan(radians(self.angle)), cladding_thickness)\
                             << QPoint((film_width-wg_width)/2+wg_height/tan(radians(self.angle)),cladding_thickness)\
                             << QPoint((film_width-wg_width)/2,cladding_thickness+wg_height) << QPoint(0, cladding_thickness+wg_height)\
                             << QPoint(0, cladding_thickness+film_thickness)\
                             << QPoint(film_width, cladding_thickness+film_thickness)
        
                             
        self._substrate_poly = QtGui.QPolygonF()
        self._substrate_poly << QPoint(0, cladding_thickness+film_thickness)\
                             << QPoint(film_width, cladding_thickness+film_thickness)\
                             << QPoint(film_width, cladding_thickness+film_thickness+substrate_thickness)\
                             << QPoint(0, cladding_thickness+film_thickness+substrate_thickness)
        
        
    def _constructParts(self):
        self._claddingPart = _PolyPart(self._cladding_poly, 
                                       STYLESHEET['background-cladding'],
                                       STYLESHEET['hover-cladding'])
        self._waveguidePart = _PolyPart(self._waveguide_poly, 
                                        STYLESHEET['background-waveguide'],
                                        STYLESHEET['hover-waveguide'])
        self._substratePart = _PolyPart(self._substrate_poly, 
                                        STYLESHEET['background-substrate'],
                                        STYLESHEET['hover-substrate'])
    
    def paintEvent(self, a0: QPaintEvent) -> None:
        self.painter = QtGui.QPainter(self)
        
        
        self._constructPolys(self.painter.device().width(), self.painter.device().height())
        self._claddingPart.poly = self._cladding_poly
        self._waveguidePart.poly = self._waveguide_poly
        self._substratePart.poly = self._substrate_poly
        
        self._claddingPart.paint(self.painter)
        self._waveguidePart.paint(self.painter)
        self._substratePart.paint(self.painter)
        self.painter.end()
        
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if self._claddingPart.detect_mouse_pressed(a0):
            self._waveguidePart.reset()
            self._substratePart.reset()
            self.cladding_toggled.emit()
        if self._waveguidePart.detect_mouse_pressed(a0):
            self._claddingPart.reset()
            self._substratePart.reset()
            self.waveguide_toggled.emit()
        if self._substratePart.detect_mouse_pressed(a0):
            self._waveguidePart.reset()
            self._claddingPart.reset()
            self.substrate_toggled.emit()
        self.update()
        
class _PolyPart():
    def __init__(self, poly: QtGui.QPolygonF, 
                 background_color,
                 hover_color) -> None:
        self._poly = poly
        self.background_color = background_color
        self.hover_color = hover_color
        
        self.path = QtGui.QPainterPath()
        self.path.addPolygon(self._poly)
        
        self.brush = QtGui.QBrush()
        self.brush.setColor(QtGui.QColor(background_color))
        self.brush.setStyle(Qt.DiagCrossPattern)
        
        self.pressed = False
        self.hover = False
    
    @property
    def poly(self):
        return self._poly
    
    @poly.setter
    def poly(self, value):
        self._poly = value
        self.path = QtGui.QPainterPath()
        self.path.addPolygon(self._poly)
        
    def paint(self, painter: QtGui.QPainter):
        painter.drawPolygon(self.poly)
        painter.fillPath(self.path, self.brush)
        
        
    def detect_mouse_pressed(self, a: QMouseEvent) -> bool:
        if self.poly.containsPoint(a.pos(), Qt.OddEvenFill):
            if self.pressed:
                self.pressed = False
                self.brush.setStyle(Qt.DiagCrossPattern)
            else:
                self.pressed = True
                self.brush.setStyle(Qt.SolidPattern)
        return self.pressed
    
    #TODO: mathe figure out how to do hover updates       
    def detect_mouse_hover(self, a: QMouseEvent):
        if self.poly.containsPoint(a.pos(), Qt.OddEvenFill):
            if self.pressed:
                self.pressed = False
                self.brush.setStyle(Qt.DiagCrossPattern)
            else:
                self.pressed = True
                self.brush.setStyle(Qt.SolidPattern)
        return self.hover
                
    def reset(self):
        self.pressed = False
        self.brush.setStyle(Qt.DiagCrossPattern)
        
class ProcessFormWidget(QtWidgets.QWidget, Ui_ProcessForm):
    dataChanged = pyqtSignal()
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.doubleSpinBoxPumpCenter.valueChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxPumpBandwidth.valueChanged.connect(self.dataChanged.emit)
        self.comboBoxPumpType.currentTextChanged.connect(self.dataChanged.emit)
        self.comboBoxPumpPol.currentTextChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxSignalCenter.valueChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxSignalWidth.valueChanged.connect(self.dataChanged.emit)
        self.comboBoxSignalPol.currentTextChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxIdlerCenter.valueChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxIdlerWidth.valueChanged.connect(self.dataChanged.emit)
        self.comboBoxIdlerPol.currentTextChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxSignalFilterCenter.valueChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxSignalFilterWidth.valueChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxIdlerFilterCenter.valueChanged.connect(self.dataChanged.emit)
        self.doubleSpinBoxIdlerFilterWidth.valueChanged.connect(self.dataChanged.emit)
        self.groupBoxFilters.toggled.connect(self.dataChanged.emit)
    
    def loadToProfile(self, profile: SetupProfile):
        profile.pumpCenter = self.doubleSpinBoxPumpCenter.value()
        profile.pumpBandwidth = self.doubleSpinBoxPumpBandwidth.value()
        profile.pumpType = str(self.comboBoxPumpType.currentText())
        profile.pumpPol = self.comboBoxPumpPol.currentText()
        profile.signalCenter = self.doubleSpinBoxSignalCenter.value()
        profile.signalWidth = self.doubleSpinBoxSignalWidth.value()
        profile.signalPol = self.comboBoxSignalPol.currentText()
        profile.idlerCenter = self.doubleSpinBoxIdlerCenter.value()
        profile.idlerWidth = self.doubleSpinBoxIdlerWidth.value()
        profile.idlerPol = self.comboBoxIdlerPol.currentText()
        profile.signalFilterCenter = self.doubleSpinBoxSignalFilterCenter.value()
        profile.signalFilterWidth = self.doubleSpinBoxSignalFilterWidth.value()
        profile.idlerFilterCenter = self.doubleSpinBoxIdlerFilterCenter.value()
        profile.idlerFilterWidth = self.doubleSpinBoxIdlerFilterWidth.value()
        
        if not self.groupBoxFilters.isChecked():
            profile.signalFilterCenter = self.doubleSpinBoxSignalCenter.value()
            profile.signalFilterWidth = self.doubleSpinBoxSignalWidth.value()
            profile.idlerFilterCenter = self.doubleSpinBoxIdlerCenter.value()
            profile.idlerFilterWidth = self.doubleSpinBoxIdlerWidth.value()
    
    def loadFromProfile(self, profile: SetupProfile):
        self.doubleSpinBoxPumpCenter.setValue(profile.pumpCenter)
        self.doubleSpinBoxPumpBandwidth.setValue(profile.pumpBandwidth)
        self.comboBoxPumpType.setCurrentText(profile.pumpType)
        self.comboBoxPumpPol.setCurrentText(profile.pumpPol)
        self.doubleSpinBoxSignalCenter.setValue(profile.signalCenter)
        self.doubleSpinBoxSignalWidth.setValue(profile.signalWidth)
        self.comboBoxSignalPol.setCurrentText(profile.signalPol)
        self.doubleSpinBoxIdlerCenter.setValue(profile.idlerCenter)
        self.doubleSpinBoxIdlerWidth.setValue(profile.idlerWidth)
        self.comboBoxIdlerPol.setCurrentText(profile.idlerPol)
        self.doubleSpinBoxSignalFilterCenter.setValue(profile.signalFilterCenter)
        self.doubleSpinBoxSignalFilterWidth.setValue(profile.signalFilterWidth)
        self.doubleSpinBoxIdlerFilterCenter.setValue(profile.idlerFilterCenter)
        self.doubleSpinBoxIdlerFilterWidth.setValue(profile.idlerFilterWidth)

"""class DatabaseSelectorWidget(QtWidgets.QWidget, Ui_DatabaseSelector):
    
    saveUpdateButtonPressed = pyqtSignal()
    deleteButtonPressed = pyqtSignal()
    retrieveButtonPressed = pyqtSignal(Profile)
    
    def __init__(self, table: str,  *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.model = DatabaseListModel(table)
        self.listViewDatabase.setModel(self.model)
        
        self.pushButtonDelete.clicked.connect(self.onDeleteButtonPressed)
        self.pushButtonSaveUpdate.clicked.connect(self.onSaveUpdateButtonPressed)
        self.pushButtonRetrieve.clicked.connect(self.onRetrieveButtonPressed)
        
    def onDeleteButtonPressed(self):
        index = self.listViewDatabase.selectedIndexes()[0]
        self.model.table.delete(self.model.data(index, Qt.DisplayRole))
        self.model.layoutChanged.emit()
        self.listViewDatabase.clearSelection()
        self.deleteButtonPressed.emit()
        
    def onSaveUpdateButtonPressed(self):
        self.saveUpdateButtonPressed.emit()
        
    def onRetrieveButtonPressed(self):
        index = self.listViewDatabase.selectedIndexes()[0]
        data = self.model.table.get(self.model.data(index, Qt.DisplayRole))
        self.model.layoutChanged.emit()
        self.listViewDatabase.clearSelection()
        self.retrieveButtonPressed.emit(ProcessProfile(data = data))"""
        
"""class ProcessFormDatabaseWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.verticalLayout = QtWidgets.QHBoxLayout(self)
        self.processForm = ProcessFormWidget()
        self.databaseSelector = DatabaseSelectorWidget("process")
        self.verticalLayout.addWidget(self.processForm)
        self.verticalLayout.addWidget(self.databaseSelector)
        
        self.databaseSelector.saveUpdateButtonPressed.connect(self.saveUpdate)
        self.databaseSelector.retrieveButtonPressed.connect(self.processForm.setProfile)
        
    def saveUpdate(self):
        profile = self.processForm.getProfile()
        profile.save()
        self.databaseSelector.model.layoutChanged.emit()
        self.databaseSelector.listViewDatabase.clearSelection()"""
        
class DispersionFormWidget(QtWidgets.QWidget, Ui_DispersionForm):
    dataChanged = pyqtSignal()
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.table = PyJSATable("dispersion")
        
        self.comboBoxType.addItems(self.table.get_unique_column("type"))
        self.comboBoxFilmThickness.addItems(map(str, self.table.get_unique_column("filmThickness")))
        self.comboBoxHeight.addItems(map(str, self.table.get_unique_column("height")))
        self.comboBoxWidth.addItems(map(str, self.table.get_unique_column("width")))
        self.comboBoxCladding.addItems(map(str, self.table.get_unique_column("cladding")))
        self.comboBoxCore.addItems(map(str, self.table.get_unique_column("material")))
        self.comboBoxSubstrate.addItems(map(str, self.table.get_unique_column("substrate")))
        self.comboBoxTemperature.addItems(map(str, self.table.get_unique_column("temperature")))
        
        self.onFilmthicknessChanged(self.comboBoxFilmThickness.currentText())
        self.refreshDispersionPlot()
        
        self.comboBoxFilmThickness.currentTextChanged.connect(self.onFilmthicknessChanged)
        
        self.comboBoxCladding.currentTextChanged.connect(self.refreshDispersionPlot)
        self.comboBoxType.currentTextChanged.connect(self.refreshDispersionPlot)
        self.comboBoxHeight.currentIndexChanged.connect(self.refreshDispersionPlot)
        self.comboBoxWidth.currentTextChanged.connect(self.refreshDispersionPlot)
        self.comboBoxSubstrate.currentTextChanged.connect(self.refreshDispersionPlot)
        self.comboBoxCore.currentTextChanged.connect(self.refreshDispersionPlot)
        self.comboBoxTemperature.currentTextChanged.connect(self.refreshDispersionPlot)
        
    def onFilmthicknessChanged(self, newValue: str):
        for i in range(self.comboBoxHeight.count()):
            if float(self.comboBoxHeight.model().item(i).text()) >= float(newValue):
                self.comboBoxHeight.model().item(i).setEnabled(False)
            else:
                self.comboBoxHeight.model().item(i).setEnabled(True)
        self.comboBoxHeight.setCurrentIndex(0)
        self.refreshDispersionPlot()
        
                
    def getDispersionProfile(self):
        pk=(self.comboBoxType.currentText(), 
            float(self.comboBoxFilmThickness.currentText()), 
            float(self.comboBoxWidth.currentText()), 
            float(self.comboBoxHeight.currentText()), 
            self.comboBoxCladding.currentText(), 
            self.comboBoxCore.currentText(), 
            self.comboBoxSubstrate.currentText(), 
            float(self.comboBoxTemperature.currentText()))
        
        data = self.table.get(pk)
        return DispersionProfile(data)
    
    def loadToProfile(self, profile: SetupProfile):
        profile.dispersion = self.getDispersionProfile()
    
    def loadFromProfile(self, profile: SetupProfile):
        dispersionProfile = profile.dispersion
        self.comboBoxType.setCurrentText(str(dispersionProfile.type))
        self.comboBoxFilmThickness.setCurrentText(str(dispersionProfile.filmThickness))
        self.comboBoxWidth.setCurrentText(str(dispersionProfile.width))
        self.comboBoxHeight.setCurrentText(str(dispersionProfile.height))
        self.comboBoxCladding.setCurrentText(str(dispersionProfile.cladding))
        self.comboBoxCore.setCurrentText(str(dispersionProfile.material))
        self.comboBoxSubstrate.setCurrentText(str(dispersionProfile.substrate))
        self.comboBoxTemperature.setCurrentText(str(dispersionProfile.temperature))
    
    def refreshDispersionPlot(self):
        self.dataChanged.emit()
        dispersionProfile = self.getDispersionProfile()
        self.dispersionPlotWidget.clear()
        self.dispersionPlotWidget.getPlotItem().plot(dispersionProfile.wavelengths, dispersionProfile.neffsTE)
        self.dispersionPlotWidget.getPlotItem().plot(dispersionProfile.wavelengths, dispersionProfile.neffsTM)
        
class PolingFormWidget(QtWidgets.QWidget, Ui_PolingForm):
    dataChanged = pyqtSignal()
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.pushButtonGaussian.clicked.connect(self.fromProcessGaussian)
        self.pushButtonRegular.clicked.connect(self.fromProcessRegular)
        self.pushButtonFromTPM.clicked.connect(self.fromTPM)
        self._profile = None
    
    def fromProcessGaussian(self):
        domainsNumber = 2*int(self.doubleSpinBoxLength.value()*1e3/self.polingPeriod)
        self.domains = np.ones(domainsNumber)*self.polingPeriod/2
        self.orientation = findGaussianProfile(self.doubleSpinBoxLength.value()*1e3, self.polingPeriod, pmfGaussian, self.doubleSpinBoxLength.value()*1e3)
        
        self.refreshPlot()
        
    
    def fromProcessRegular(self):
        domainsNumber = int(2*self.doubleSpinBoxLength.value()*1e3/self.polingPeriod)
        print(self.polingPeriod)
        self.domains = np.ones(domainsNumber)*self.polingPeriod/2
        self.orientation = np.empty((domainsNumber,))
        self.orientation[::2] = 1
        self.orientation[1::2] = -1
        
        self.refreshPlot()
    
    def fromTPM(self):
        pass
    
    def loadFromProfile(self, profile: SetupProfile):
        self.orientation = profile.orientation
        self.domains = profile.domains
        self.polingPeriod = profile.getPolingPeriod()
        self.refreshPlot()
    
    def loadToProfile(self, profile: SetupProfile):
        profile.orientation = self.orientation
        profile.domains = self.domains
        
    def setPolingFromProfile(self, profile: SetupProfile):
        self.polingPeriod = profile.getPolingPeriod()
    
    def refreshPlot(self):
        self.dataChanged.emit()
        image = pqg.ImageItem(np.transpose(100*np.tile(self.orientation,(100,1))), colorMap = 'CET-C3')
        self.plotWidgetPoling.clear()
        self.plotWidgetPoling.addItem(image)