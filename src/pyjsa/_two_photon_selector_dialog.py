from PyQt5 import QtGui
from PyQt5.QtWidgets import*
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject
import sys
from pyjsa.assets.ui.Ui_two_photon_selector_dialog import Ui_TwoPhotonSelectorDialog
import pyqtgraph as pqg
import cv2
import numpy as np
from scipy.signal import find_peaks

class TwoPhotonSelectorDialog(Ui_TwoPhotonSelectorDialog):
    def setupUi(self, Dialog: QDialog):
        super().setupUi(Dialog)
        self.binarized = False
        self.path = None
        
        self.open_image_button.clicked.connect(self.open_image)
        self.binarize_button.clicked.connect(self.on_binarize_button_clicked)
        self.bin_threshold_slider.sliderMoved.connect(self.on_bin_slider_moved)
        self.slider_peak_height.sliderMoved.connect(self.refresh_peak_analysis)
        self.spinBoxScale.valueChanged.connect(lambda x: self.spinBoxWidth.setValue(self.spinBoxWidth.value()*x))
        
    
    def on_roi_changed(self):
        self.zoom_img_array = self.two_photon_roi.getArrayRegion(self.img_array, self.img_item).astype(np.uint8)
        self.zoom_image_item = pqg.ImageItem(image = self.zoom_img_array)
        self.zoom_image.clear()
        self.zoom_image.addItem(self.zoom_image_item)
        
        self.spinBoxWidth.setValue(self.two_photon_roi.size()[1]*self.spinBoxScale.value())
        self.spinBoxLength.setValue(self.two_photon_roi.size()[0]*self.spinBoxScale.value()*1e-3)
        
        if self.binarized: self.refresh_peak_analysis()
        
    def on_binarize_button_clicked(self):
        if self.binarized:
            self.binarized = False
            self.binarize_button.setStyleSheet("background-color : ")
            self.bin_threshold_slider.setEnabled(False)
            self.refresh_plots(self.img)
            self.peaks_plot.clear()
            self.profile_plot.clear()
        else:
            self.binarized = True
            self.binarize_button.setStyleSheet("background-color : green")
            self.bin_threshold_slider.setEnabled(True)
            self.refresh_plots(self.bin_img)
            self.refresh_peak_analysis()
            
            
    def refresh_plots(self, img, opened = False):
        self.img_array = np.array(img)
        self.img_item = pqg.ImageItem(image=self.img_array)
        self.two_photon_image.clear()
        self.two_photon_image.setAspectLocked(1/4)
        self.two_photon_image.addItem(self.img_item)
        
        if opened:
            self.two_photon_roi = pqg.RectROI((0,500), (self.img_array.shape[1], 20), 
                                              resizable = True,
                                              rotatable = False,
                                              scaleSnap = True,
                                              translateSnap = True)
            self.two_photon_roi.addScaleHandle([0,1],[1,1])
            self.two_photon_roi.removeHandle(0)
            self.two_photon_roi.addScaleHandle([1,1],[0,1])
        self.two_photon_image.addItem(self.two_photon_roi)
        
        self.zoom_img_array = self.two_photon_roi.getArrayRegion(self.img_array, self.img_item).astype(np.uint8)
        self.zoom_image_item = pqg.ImageItem(image = self.zoom_img_array)
        self.zoom_image.clear()
        self.zoom_image.setAspectLocked(1/4)
        self.zoom_image.addItem(self.zoom_image_item)
            
            
    def refresh_peak_analysis(self):
        self.peaks_plot.clear()
        self.summed_image = np.sum(255 - self.zoom_img_array, axis = 0)
        self.peaks_plot.getPlotItem().plot(self.summed_image)
        self.peaks_pos, self.peaks_prop = find_peaks(self.summed_image, self.slider_peak_height.value())
        self.peaks_plot.getPlotItem().plot(self.peaks_pos, self.peaks_prop['peak_heights'], pen = None, symbol = 'd')
        
        self.domain_widths = np.gradient(self.peaks_pos)
        self.profile_plot.clear()
        self.profile_plot.getPlotItem().plot(self.domain_widths)
        
    def open_image(self):
        file_dialog = QFileDialog()
        self.path = file_dialog.getOpenFileName()[0]
        self.img = cv2.imread(self.path)
        
        #binarize
        self.bin_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, self.bin_img = cv2.threshold(self.bin_img, self.bin_threshold_slider.value(), 255,cv2.THRESH_BINARY)
        
        self.refresh_plots(self.img, opened=True)
        self.two_photon_roi.sigRegionChanged.connect(self.on_roi_changed)
        self.binarize_button.setEnabled(True)
        
        self.slider_peak_height.setEnabled(True)
        self.slider_peak_height.setMinimum(0)
        self.slider_peak_height.setMaximum((self.zoom_img_array.shape[0]-1)*255)
        self.slider_peak_height.setValue((self.zoom_img_array.shape[0]-1)*255)
        
        self.spinBoxScale.setEnabled(True)
        self.spinBoxLength.setEnabled(True)
        self.spinBoxWidth.setEnabled(True)
        self.spinBoxWidth.setValue(self.two_photon_roi.size()[1]*self.spinBoxScale.value())
        self.spinBoxLength.setValue(self.two_photon_roi.size()[0]*self.spinBoxScale.value()*1e-3)
        
        self.spinBoxScale.valueChanged.connect(self.onScaleChanged)
        
    def on_bin_slider_moved(self):
        self.bin_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, self.bin_img = cv2.threshold(self.bin_img, self.bin_threshold_slider.value(), 255, cv2.THRESH_BINARY)
        
        self.refresh_plots(self.bin_img)
        self.refresh_peak_analysis()
        
    def onScaleChanged(self):
        self.spinBoxWidth.setValue(self.two_photon_roi.size()[1]*self.spinBoxScale.value())
        self.spinBoxLength.setValue(self.two_photon_roi.size()[0]*self.spinBoxScale.value()*1e-3)
        
    
        
        