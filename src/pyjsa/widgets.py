import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QEvent, QPoint, pyqtSignal
from PyQt5.QtGui import QPaintEvent, QMouseEvent
from math import tan, radians

from PyQt5.QtWidgets import QWidget

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
