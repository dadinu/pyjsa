from PyQt5 import QtGui
from PyQt5.QtWidgets import*
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject
import sys
from pyjsa.assets.ui.Ui_main_window_graph import Ui_MainWindow_graph
from pyjsa.waveguide import Waveguide
from pyjsa.pump import Pump
from pyjsa.experiment import Experiment, find_optimal_pump_width
from pyjsa._workers import WorkerExperiment
import pyqtgraph as pqg
import numpy as np
from configparser import ConfigParser
import traceback

pqg.setConfigOptions(imageAxisOrder = 'row-major')

class MainWindow(Ui_MainWindow_graph, QMainWindow):
    def setupUi(self, Window: QMainWindow):
        super().setupUi(Window)
        
        #
        #Threads and workers
        #
        self.threadpool = QThreadPool()
        
        #
        # Initial Plots
        #
        self.set_pyjsa_objects()
        
        
        #
        # Signals
        #
        self.waveguide_params_top.children()[0].sigValueChanged.connect(self.film_thickness_changed)
        self.idler_edit.valueChanged.connect(self.signal_or_idler_changed)
        self.signal_edit.valueChanged.connect(self.signal_or_idler_changed)
        self.jsa_roi.sigRegionChangeFinished.connect(self.filters_changed_roi)
        self.filters_params_top.sigTreeStateChanged.connect(self.filters_changed_tree)
        self.reset_filters_button.clicked.connect(self.reset_filters)
        self.actionRun_experiment.triggered.connect(self.set_pyjsa_objects)
        self.actionAdjust_pump_width.triggered.connect(self.adjust_pump)
        self.waveguide_params_top.children()[4].sigStateChanged.connect(self.plot_waveguide_profile)
        self.actionSave_As.triggered.connect(self.save_config_as)
        self.actionOpen.triggered.connect(self.open_config)
        
    def process_result(self, result):
        self.pef = result[0]
        self.pmf = result[1]
        self.jsa = result[2]
        self.signal_passes = result[3]
        self.idler_passes = result[4]
        self.both_pass = result[5]
        self.s_values = result[6]
        self.purity = result[7]
        
    
    def set_pyjsa_objects(self):
        #waveguide variables
        thickness = self.waveguide_params_top.children()[0].value()
        width = int(np.around(np.around(self.waveguide_params_top.children()[1].value(), 1)/0.1, 0)) - 5
        height = int(np.around(np.around(self.waveguide_params_top.children()[2].value(), 1)/0.1, 0)) - 2
        length = self.waveguide_params_top.children()[3].value()*1e-3
        profile = self.profiles_array.index(self.waveguide_params_top.children()[4].value())
        
        #pump variables
        width_pump = self.pump_params_top.children()[1].value()*1e-9
        
        #experiment variables
        self.signal = [self.signal_edit.value()*1e-9, 20e-9]
        self.idler = [self.idler_edit.value()*1e-9, 20e-9]
        
        #filter variables
        filter_signal_center = self.filters_params_top.children()[0].value()*1e-9
        filter_signal_width = self.filters_params_top.children()[1].value()*1e-9
        filter_idler_center = self.filters_params_top.children()[2].value()*1e-9
        filter_idler_width = self.filters_params_top.children()[3].value()*1e-9
        
        filters = [filter_signal_width, filter_idler_width, filter_signal_center, filter_idler_center]
        
        #pyjsa objects
        self.waveguide = Waveguide(thickness, width, height, length, profile=profile)
        self.pump = Pump(width_pump)
        self.experiment = Experiment(self.waveguide, 
                                     self.pump, 
                                     self.signal, 
                                     self.idler, 
                                     self.signal_pol_selector.currentText(),
                                     self.idler_pol_selector.currentText(),
                                     self.pump_pol_selector.currentText())
        
        self.pyjsa_worker = WorkerExperiment(self.experiment, filters)
        self.pyjsa_worker.signals.progress.connect(self.progress.setValue)
        self.pyjsa_worker.signals.result.connect(self.process_result)
        self.pyjsa_worker.signals.finished.connect(self.refresh_plots)
        self.progress.setVisible(True)
        self.threadpool.start(self.pyjsa_worker)
        
    #
    # Slots
    #  
     
    def refresh_plots(self):
        self.progress.setVisible(False)
        self.reset_filters()
        
        #actual plotting
        tr = QtGui.QTransform() # transform to translate the images
        scale_x = self.signal[1]*1e9/1000
        scale_y = self.idler[1]*1e9/1000
        tr.translate((self.signal[0]*1e9-self.signal[1]/2*1e9)/scale_x, (self.idler[0]*1e9-self.idler[1]/2*1e9)/scale_y)
        
        #pef
        image_pef = pqg.ImageItem(image = self.pef, colorMap = 'inferno')
        image_pef.setTransform(tr)
        image_pef_phase = pqg.ImageItem(image = np.angle(self.pef, deg=True), colorMap = 'inferno')
        image_pef_phase.setTransform(tr)
        self.pump_plot.clear()
        self.pump_plot.addItem(image_pef)
        self.pump_plot.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.pump_plot.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.pump_plot.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.pump_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.pump_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        self.pump_plot.getPlotItem().setTitle('Norm')
        
        self.pump_plot_phase.clear()
        self.pump_plot_phase.addItem(image_pef_phase)
        self.pump_plot_phase.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.pump_plot_phase.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.pump_plot_phase.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.pump_plot_phase.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.pump_plot_phase.getPlotItem().setMouseEnabled(x = False, y = False)
        self.pump_plot_phase.getPlotItem().setTitle('Phase')
                
        #pmf
        image_pmf = pqg.ImageItem(image = np.abs(self.pmf), colorMap = 'inferno')
        image_pmf.setTransform(tr)
        image_pmf_phase = pqg.ImageItem(image = np.angle(self.pmf, deg=True), colorMap = 'inferno')
        image_pmf_phase.setTransform(tr)
        self.pmf_plot.clear()
        self.pmf_plot.addItem(image_pmf)
        self.pmf_plot.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.pmf_plot.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.pmf_plot.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.pmf_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.pmf_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        self.pmf_plot.getPlotItem().setTitle('Norm')
        
        self.pmf_plot_phase.clear()
        self.pmf_plot_phase.addItem(image_pmf_phase)
        self.pmf_plot_phase.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.pmf_plot_phase.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.pmf_plot_phase.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.pmf_plot_phase.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.pmf_plot_phase.getPlotItem().setMouseEnabled(x = False, y = False)
        self.pmf_plot_phase.getPlotItem().setTitle('Phase')
        
        image_profile = pqg.ImageItem(image = 100*np.tile(self.experiment.waveguide.g(poling_period=self.experiment.poling_period), (100,1)), colorMap = 'CET-C3')
        self.waveguide_profile_plot.clear()
        self.waveguide_profile_plot.addItem(image_profile)
        self.waveguide_profile_plot.setMouseEnabled(x = True, y = True)
        
        #jsa
        image_jsa = pqg.ImageItem(image = np.abs(self.jsa), colorMap = 'inferno')
        image_jsa.setTransform(tr)
        image_jsa_phase = pqg.ImageItem(image = np.angle(self.jsa, deg=True), colorMap = 'inferno')
        image_jsa_phase.setTransform(tr)
        self.jsa_plot.clear()
        self.jsa_plot.addItem(image_jsa)
        self.jsa_plot.addItem(self.jsa_roi)
        self.jsa_plot.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.jsa_plot.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.jsa_plot.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.jsa_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.jsa_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        self.jsa_plot.getPlotItem().setTitle('Norm')
        
        self.jsa_plot_phase.clear()
        self.jsa_plot_phase.addItem(image_jsa_phase)
        self.jsa_plot_phase.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.jsa_plot_phase.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.jsa_plot_phase.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.jsa_plot_phase.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.jsa_plot_phase.getPlotItem().setMouseEnabled(x = False, y = False)
        self.jsa_plot_phase.getPlotItem().setTitle('Phase')  
        
        self.jsa_roi.setPos((tr.dx(), tr.dy()))
        
        #schmidt values
        bar_schmidt = pqg.BarGraphItem(x = range(20), height = self.s_values[:20], width = 0.5)
        self.schmidt_plot.clear()
        self.schmidt_plot.addItem(bar_schmidt)
        self.schmidt_plot.getPlotItem().setLabel(axis = 'left', text = 'Schmidt value')
        self.schmidt_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Value index')
        self.schmidt_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        
        self.exp_stat_params_top.children()[0].setValue(self.signal_passes/self.both_pass*100)
        self.exp_stat_params_top.children()[1].setValue(self.idler_passes/self.both_pass*100)
        self.exp_stat_params_top.children()[2].setValue(self.signal_passes*self.idler_passes/self.both_pass**2*100)
        self.exp_stat_params_top.children()[3].setValue(self.purity*100)
        self.exp_stat_params_top.children()[4].setValue(self.experiment.poling_period*1e6)
    
    def film_thickness_changed(self):
        if self.waveguide_params_top.children()[2].value() >= self.waveguide_params_top.children()[0].value():
            self.waveguide_params_top.children()[2].setValue(self.waveguide_params_top.children()[0].value()-0.1)
        self.waveguide_params_top.children()[2].setLimits([0.2, self.waveguide_params_top.children()[0].value()-0.1])
    
    def signal_or_idler_changed(self):
        self.pump_params_top.children()[0].setValue(1/(1/self.idler_edit.value()+1/self.signal_edit.value()))
    
    def filters_changed_roi(self):
        if self.tab_jsa.currentIndex() == 0:
            scale = 20/1000
            
            filter_signal_width = self.jsa_roi.size()[0]*scale
            filter_signal_center = (self.jsa_roi.pos()[0]+self.jsa_roi.size()[0]/2)*scale
            filter_idler_width = self.jsa_roi.size()[1]*scale
            filter_idler_center = (self.jsa_roi.pos()[1]+self.jsa_roi.size()[1]/2)*scale
            filters = [filter_signal_width*1e-9, filter_idler_width*1e-9, filter_signal_center*1e-9, filter_idler_center*1e-9]
            
            self.filters_params_top.children()[0].setValue(filter_signal_center)
            self.filters_params_top.children()[1].setValue(filter_signal_width)
            self.filters_params_top.children()[2].setValue(filter_idler_center)
            self.filters_params_top.children()[3].setValue(filter_idler_width)
            
            #update schmidt values and experiment statistics
            self.jsa, signal_passes, idler_passes, both_pass = self.experiment.joint_spectral_amplitude(filters)
            s_values, purity = self.experiment.schmidt_decomposition(filters)
            
            bar_schmidt = pqg.BarGraphItem(x = range(20), height = s_values[:20], width = 0.5)
            self.schmidt_plot.clear()
            self.schmidt_plot.addItem(bar_schmidt)
            self.schmidt_plot.getPlotItem().setLabel(axis = 'left', text = 'Schmidt value')
            self.schmidt_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Value index')
            self.schmidt_plot.getPlotItem().setMouseEnabled(x = False, y = False)
            
            self.exp_stat_params_top.children()[0].setValue(both_pass/signal_passes*100)
            self.exp_stat_params_top.children()[1].setValue(both_pass/idler_passes*100)
            self.exp_stat_params_top.children()[2].setValue(both_pass**2/idler_passes/signal_passes*100)
            self.exp_stat_params_top.children()[3].setValue(purity*100)
        
    def filters_changed_tree(self):
        if self.tab_jsa.currentIndex() == 1:
            scale = 20/1000
            
            filter_signal_center = self.filters_params_top.children()[0].value()
            filter_signal_width = self.filters_params_top.children()[1].value()
            filter_idler_center = self.filters_params_top.children()[2].value()
            filter_idler_width = self.filters_params_top.children()[3].value()
            filters = [filter_signal_width*1e-9, filter_idler_width*1e-9, filter_signal_center*1e-9, filter_idler_center*1e-9]
            
            self.jsa_roi.setSize((filter_signal_width/scale, filter_idler_width/scale))
            self.jsa_roi.setPos(((filter_signal_center-filter_signal_width/2)/scale, (filter_idler_center-filter_idler_width/2)/scale))
            
            #update schmidt values and experiment statistics
            self.jsa, signal_passes, idler_passes, both_pass = self.experiment.joint_spectral_amplitude(filters)
            s_values, purity = self.experiment.schmidt_decomposition(filters)
            
            bar_schmidt = pqg.BarGraphItem(x = range(20), height = s_values[:20], width = 0.5)
            self.schmidt_plot.clear()
            self.schmidt_plot.addItem(bar_schmidt)
            self.schmidt_plot.getPlotItem().setLabel(axis = 'left', text = 'Schmidt value')
            self.schmidt_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Value index')
            self.schmidt_plot.getPlotItem().setMouseEnabled(x = False, y = False)
            
            self.exp_stat_params_top.children()[0].setValue(both_pass/signal_passes*100)
            self.exp_stat_params_top.children()[1].setValue(both_pass/idler_passes*100)
            self.exp_stat_params_top.children()[2].setValue(both_pass**2/idler_passes/signal_passes*100)
            self.exp_stat_params_top.children()[3].setValue(purity*100)

    def reset_filters(self):
        self.filters_params_top.children()[0].setValue(self.signal_edit.value())
        self.filters_params_top.children()[1].setValue(20)
        self.filters_params_top.children()[2].setValue(self.idler_edit.value())
        self.filters_params_top.children()[3].setValue(20)
        scale = 20/1000
        self.jsa_roi.setSize((20/scale, 20/scale))
        self.jsa_roi.setPos(((self.signal_edit.value()-20/2)/scale, (self.idler_edit.value()-20/2)/scale))
        
    def adjust_pump(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.reset_filters()
        filter_signal_center = self.filters_params_top.children()[0].value()
        filter_signal_width = self.filters_params_top.children()[1].value()
        filter_idler_center = self.filters_params_top.children()[2].value()
        filter_idler_width = self.filters_params_top.children()[3].value()
        filters = [filter_signal_width*1e-9, filter_idler_width*1e-9, filter_signal_center*1e-9, filter_idler_center*1e-9]
        
        res = find_optimal_pump_width(self.experiment, [0.1, 10], filters)
        self.experiment.pump.width = res.x*1e-9
        self.pump_params_top.children()[1].setValue(res.x)
        
        #update pump, jsa and schmidt plots
        
        self.pef = self.experiment.pump.pump_envelope_function()
        self.jsa, signal_passes, idler_passes, both_pass = self.experiment.joint_spectral_amplitude(filters)
        s_values, purity = self.experiment.schmidt_decomposition(filters)
        
        signal = [self.signal_edit.value()*1e-9, 20e-9]
        idler = [self.signal_edit.value()*1e-9, 20e-9]
        
        tr = QtGui.QTransform() # transform to translate the images
        scale_x = signal[1]*1e9/1000
        scale_y = idler[1]*1e9/1000
        tr.translate((signal[0]*1e9-signal[1]/2*1e9)/scale_x, (idler[0]*1e9-idler[1]/2*1e9)/scale_y)
        
        #pef
        image_pef = pqg.ImageItem(image = self.pef, colorMap = 'inferno')
        image_pef.setTransform(tr)
        image_pef_phase = pqg.ImageItem(image = np.angle(self.pef, deg=True), colorMap = 'inferno')
        image_pef_phase.setTransform(tr)
        self.pump_plot.clear()
        self.pump_plot.addItem(image_pef)
        self.pump_plot.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.pump_plot.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.pump_plot.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.pump_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.pump_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        self.pump_plot.getPlotItem().setTitle('Norm')
        
        self.pump_plot_phase.clear()
        self.pump_plot_phase.addItem(image_pef_phase)
        self.pump_plot_phase.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.pump_plot_phase.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.pump_plot_phase.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.pump_plot_phase.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.pump_plot_phase.getPlotItem().setMouseEnabled(x = False, y = False)
        self.pump_plot_phase.getPlotItem().setTitle('Phase')
        
        #jsa
        image_jsa = pqg.ImageItem(image = np.abs(self.jsa), colorMap = 'inferno')
        image_jsa.setTransform(tr)
        image_jsa_phase = pqg.ImageItem(image = np.angle(self.jsa, deg=True), colorMap = 'inferno')
        image_jsa_phase.setTransform(tr)
        self.jsa_plot.clear()
        self.jsa_plot.addItem(image_jsa)
        self.jsa_plot.addItem(self.jsa_roi)
        self.jsa_plot.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.jsa_plot.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.jsa_plot.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.jsa_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.jsa_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        self.jsa_plot.getPlotItem().setTitle('Norm')
        
        self.jsa_plot_phase.clear()
        self.jsa_plot_phase.addItem(image_jsa_phase)
        self.jsa_plot_phase.getPlotItem().getAxis('left').setScale(scale = scale_x)
        self.jsa_plot_phase.getPlotItem().getAxis('bottom').setScale(scale = scale_y)
        self.jsa_plot_phase.getPlotItem().setLabel(axis = 'left', text = 'Idler (nm)')
        self.jsa_plot_phase.getPlotItem().setLabel(axis = 'bottom', text = 'Signal (nm)')
        self.jsa_plot_phase.getPlotItem().setMouseEnabled(x = False, y = False)
        self.jsa_plot_phase.getPlotItem().setTitle('Phase')
        
        self.jsa_roi.setPos((tr.dx(), tr.dy()))
        
        #schmidt values
        bar_schmidt = pqg.BarGraphItem(x = range(20), height = s_values[:20], width = 0.5)
        self.schmidt_plot.clear()
        self.schmidt_plot.addItem(bar_schmidt)
        self.schmidt_plot.getPlotItem().setLabel(axis = 'left', text = 'Schmidt value')
        self.schmidt_plot.getPlotItem().setLabel(axis = 'bottom', text = 'Value index')
        self.schmidt_plot.getPlotItem().setMouseEnabled(x = False, y = False)
        
        self.exp_stat_params_top.children()[0].setValue(signal_passes/both_pass*100)
        self.exp_stat_params_top.children()[1].setValue(idler_passes/both_pass*100)
        self.exp_stat_params_top.children()[2].setValue(signal_passes*idler_passes/both_pass**2*100)
        self.exp_stat_params_top.children()[3].setValue(purity*100)

        QApplication.restoreOverrideCursor()
        
    def plot_waveguide_profile(self):
        profile = self.waveguide_params_top.children()[4].value()
        if profile != 'Gaussian':
            self.experiment.waveguide.profile = self.profiles_array.index(profile)
            image_profile = pqg.ImageItem(image = 100*np.tile(self.experiment.waveguide.g(poling_period=self.experiment.poling_period), (100,1)), colorMap = 'CET-C3')
            self.waveguide_profile_plot.clear()
            self.waveguide_profile_plot.addItem(image_profile)
    
    def open_config(self):
        dialog = QFileDialog()
        path = dialog.getOpenFileName(self, filter="Config (*.ini)")[0]
        if path != '':
            config = ConfigParser()
            config.read(path)
            #Process
            self.signal_pol_selector.setCurrentText(config['Process'].get('signal_pol'))
            self.idler_pol_selector.setCurrentText(config['Process'].get('idler_pol'))
            self.pump_pol_selector.setCurrentText(config['Process'].get('pump_pol'))
            self.signal_edit.setValue(config['Process'].getfloat('signal'))
            self.idler_edit.setValue(config['Process'].getfloat('idler'))
            #Pump
            self.pump_params_top.children()[0].setValue(config['Pump'].getfloat('center'))
            self.pump_params_top.children()[1].setValue(config['Pump'].getfloat('bandwidth'))
            #Waveguide
            self.waveguide_params_top.children()[0].setValue(config['Waveguide'].getfloat('film_thickness'))
            self.waveguide_params_top.children()[1].setValue(config['Waveguide'].getfloat('width'))
            self.waveguide_params_top.children()[2].setValue(config['Waveguide'].getfloat('heigth'))
            self.waveguide_params_top.children()[3].setValue(config['Waveguide'].getfloat('length'))
            self.waveguide_params_top.children()[4].setValue(config['Waveguide']['profile'])
            #Filters
            self.filters_params_top.children()[0].setValue(config['Filters'].getfloat('signal_center'))
            self.filters_params_top.children()[1].setValue(config['Filters'].getfloat('signal_width'))
            self.filters_params_top.children()[2].setValue(config['Filters'].getfloat('idler_center'))
            self.filters_params_top.children()[3].setValue(config['Filters'].getfloat('idler_width'))
            
            self.tab_jsa.setCurrentIndex(0)
            self.refresh_plots()
            
            scale = 20/1000
            filter_signal_center = config['Filters'].getfloat('signal_center')
            filter_signal_width = config['Filters'].getfloat('signal_width')
            filter_idler_center = config['Filters'].getfloat('idler_center')
            filter_idler_width = config['Filters'].getfloat('idler_width')
            
            self.jsa_roi.setSize((filter_signal_width/scale, filter_idler_width/scale))
            self.jsa_roi.setPos(((filter_signal_center-filter_signal_width/2)/scale, (filter_idler_center-filter_idler_width/2)/scale))
    
    def save_config_as(self):
        dialog = QFileDialog()
        path = dialog.getSaveFileName(self, filter="Config (*.ini)")[0]
        if path != '':
            config = ConfigParser()
            config['Process'] = {
                'signal_pol': str(self.signal_pol_selector.currentText()),
                'idler_pol': str(self.idler_pol_selector.currentText()),
                'pump_pol': str(self.pump_pol_selector.currentText()),
                'signal': str(self.signal_edit.value()),
                'idler': str(self.idler_edit.value()),
            }
            config['Pump'] = {
                'center': str(self.pump_params_top.children()[0].value()),
                'bandwidth': str(self.pump_params_top.children()[1].value())
            }
            config['Waveguide'] = {
                'film_thickness': str(self.waveguide_params_top.children()[0].value()),
                'width': str(self.waveguide_params_top.children()[1].value()),
                'heigth': str(self.waveguide_params_top.children()[2].value()),
                'length': str(self.waveguide_params_top.children()[3].value()),
                'profile': str(self.waveguide_params_top.children()[4].value())
            }
            config['Filters'] = {
                'signal_center': str(self.filters_params_top.children()[0].value()),
                'signal_width': str(self.filters_params_top.children()[1].value()),
                'idler_center': str(self.filters_params_top.children()[2].value()),
                'idler_width': str(self.filters_params_top.children()[3].value())
            }
            config['Statistics'] = {
                'signal_heralding_efficiency': str(self.exp_stat_params_top.children()[0].value()),
                'idler_heralding_efficiency': str(self.exp_stat_params_top.children()[1].value()),
                'pshe': str(self.exp_stat_params_top.children()[2].value()),
                'purity': str(self.exp_stat_params_top.children()[3].value()),
                'poling_period': str(self.exp_stat_params_top.children()[4].value())
            }
            with open(path, 'w') as configfile:
                config.write(configfile)