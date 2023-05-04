from pyjsa.assets.ui.Ui_main_window import Ui_MainWindow
from PyQt5.QtWidgets import *
from pyqtgraph.parametertree import Parameter
import pyqtgraph as pqg

class Ui_MainWindow_graph(Ui_MainWindow):
    def setupUi(self, Window: QMainWindow):
        super().setupUi(Window)
        #
        # Class variables
        #
        self.profiles_array = ["Gaussian Poled", "Gaussian", "Regular Poled"]
        self.waveguide = None
        self.pump = None
        self.experiment = None
        self.pef = None
        
        #
        # Add toolbar widget for process params.
        #
        
        self.signal_edit = QDoubleSpinBox()
        self.signal_edit.setPrefix("Signal: ")
        self.signal_edit.setSuffix(" nm")
        self.signal_edit.setMaximum(2000.0)
        self.signal_edit.setValue(1550.0)
        
        self.signal_pol_selector = QComboBox()
        self.signal_pol_selector.addItem("TE")
        self.signal_pol_selector.addItem("TM")
        self.signal_pol_selector.setEditable(False)
        
        self.idler_edit = QDoubleSpinBox()
        self.idler_edit.setPrefix("Idler: ")
        self.idler_edit.setMaximum(2000.0)
        self.idler_edit.setValue(1550.0)
        self.idler_edit.setSuffix(" nm")
        
        self.idler_pol_selector = QComboBox()
        self.idler_pol_selector.addItem("TE")
        self.idler_pol_selector.addItem("TM")
        self.idler_pol_selector.setEditable(False)
        
        self.pump_edit = QDoubleSpinBox()
        self.pump_edit.setPrefix("Pump: ")
        self.pump_edit.setSuffix(" nm")
        self.pump_edit.setMaximum(2000.0)
        self.pump_edit.setReadOnly(True)
        self.pump_edit.setValue(1/(1/self.signal_edit.value()+1/self.idler_edit.value()))
        
        self.pump_pol_selector = QComboBox()
        self.pump_pol_selector.addItem("TE")
        self.pump_pol_selector.addItem("TM")
        self.pump_pol_selector.setEditable(False)
        
        self.toolBar.addWidget(self.pump_edit)
        self.toolBar.addWidget(self.pump_pol_selector)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.signal_edit)
        self.toolBar.addWidget(self.signal_pol_selector)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.idler_edit)
        self.toolBar.addWidget(self.idler_pol_selector)
        self.toolBar.addSeparator()
        
        self.progress = QProgressBar()
        self.statusBar().addWidget(self.progress)
        self.progress.setInvertedAppearance(True)
        self.progress.setFixedWidth(300)
        self.progress.setStyleSheet("border-style: solid; border-color: grey; border-radius: 7px; border-width: 2px; text-align: center;")
        self.progress.setVisible(False)
        self.progress.setValue(0)
        
        #
        # Parameters for pump.
        #
        pump_params = [
            {'name': 'Center', 'type': 'float', 'value': 1/(1/self.idler_edit.value()+1/self.signal_edit.value()), 'readonly': True, 'suffix': 'nm'},
            {'name': 'Bandwidth', 'type': 'float', 'value': 1.75, 'suffix': 'nm'}
        ]
        self.pump_params_top = Parameter.create(name='pump_params', type = 'group', children = pump_params)
        self.pump_parameters_tree.setParameters(self.pump_params_top, showTop=False)
        
        #
        # Parameters for waveguide.
        #
        waveguide_params = [
            {'name': 'Film thickness', 'type': 'float', 'value': 0.7, 'limits': [0.3,0.8], 'step':0.1, 'suffix': 'μm'},
            {'name': 'Width', 'type': 'float', 'value': 1.2, 'limits': [0.5,2], 'step':0.1, 'suffix': 'μm'},
            {'name': 'Height', 'type': 'float', 'value': 0.3, 'limits': [0.2,0.6], 'step':0.1, 'suffix': 'μm'},
            {'name': 'Length', 'type': 'float', 'value': 5, 'limits': [0.0,20.0], 'step':1, 'suffix': 'mm'},
            {'name': 'Profile', 'type': 'list', 'values': self.profiles_array, 'value': self.profiles_array[2]}
        ]
        self.waveguide_params_top = Parameter.create(name = 'waveguide_params', type = 'group', children = waveguide_params)
        self.waveguide_tree.setParameters(self.waveguide_params_top, showTop=False)
        
        #
        # Parameters for filters
        #
        filters_params = [
            {'name': 'Signal center', 'type': 'float', 'value': 1550, 'limits': [200,2000], 'step':1, 'suffix': 'nm'},
            {'name': 'Signal width', 'type': 'float', 'value': 20, 'limits': [1,20], 'step':0.1, 'suffix': 'nm'},
            {'name': 'Idler center', 'type': 'float', 'value': 1550, 'limits': [200, 2000], 'step':1, 'suffix': 'nm'},
            {'name': 'Idler width', 'type': 'float', 'value': 20, 'limits': [1, 20], 'step':0.1, 'suffix': 'nm'},
        ]
        self.filters_params_top = Parameter.create(name = 'filters_params', type = 'group', children = filters_params)
        self.filters_tree.setParameters(self.filters_params_top, showTop=False)
        
        #
        # Parameters for experiment statistics
        #
        exp_stat_params = [
            {'name': 'Signal heralding efficiency', 'type': 'float', 'readonly': True, 'suffix': '%'},
            {'name': 'Idler heralding efficiency', 'type': 'float', 'readonly': True, 'suffix': '%'},
            {'name': 'Pair-symmetric heralding efficiency', 'type': 'float', 'readonly': True, 'suffix': '%'},
            {'name': 'Purity', 'type': 'float', 'readonly': True, 'suffix': '%'},
            {'name': 'Poling period', 'type': 'float', 'readonly': True, 'suffix':'μm'}
        ]
        self.exp_stat_params_top = Parameter.create(name = 'exp_stat_params', type = 'group', children = exp_stat_params)
        self.experiment_statistics_tree.setParameters(self.exp_stat_params_top, showTop=False)
        
        #
        # ROI for filters
        #
        self.jsa_roi = pqg.RectROI((0,0),(1000,1000))