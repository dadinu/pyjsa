from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from pyjsa.experiment import Experiment, find_optimal_pump_width
import traceback
import sys

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
        
class WorkerExperiment(QRunnable):
    def __init__(self, experiment: Experiment, filters, callback = None) -> None:
        super(WorkerExperiment, self).__init__()
        self.experiment = experiment
        self.filters = filters
        self.callback = callback
        self.signals = WorkerSignals()
    
    def run(self) -> None:
        try:
            self.experiment.pmf_callback = self.pmf_callback
            pef = self.experiment.pump.pump_envelope_function()
            pmf = self.experiment.pmf
            jsa, signal_passes, idler_passes, both_pass = self.experiment.joint_spectral_amplitude(self.filters)
            s_values, purity = self.experiment.schmidt_decomposition(self.filters)
            result = (pef, pmf, jsa, signal_passes, idler_passes, both_pass, s_values, purity)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
            
    def pmf_callback(self, p):
        self.signals.progress.emit(p)