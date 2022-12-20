"""This module is the core of the package. It contains classes and functions that aid in the computation of the PMF, JSA, Schmidt decompostion and in the optimization of the output photon spectral purity. 
"""

import numpy as np
from pyjsa.pump import Pump
from pyjsa.waveguide import Waveguide
from scipy.optimize import minimize_scalar
from scipy.special import erf
from tqdm import tqdm

def _gaussian_pmf(L, k, sigma, pol):
    dk = k-2*np.pi/pol
    a = np.exp(1j*dk*L/2)*np.sqrt(np.pi/2)*sigma*np.exp(-1/2*dk**2*sigma**2)*(erf((L-2j*dk*sigma**2)/(2*np.sqrt(2)*sigma))+erf((L+2j*dk*sigma**2)/(2*np.sqrt(2)*sigma)))
    return a

def _compute_pump_wavelength(signal, idler):
    return 1/(1/signal+1/idler)

def _compute_poling_period(signal, idler, n_signal, n_idler, n_pump) -> float:
    pump = _compute_pump_wavelength(signal, idler)
    return 1/(n_pump(pump*1e6)/pump - n_signal(signal*1e6)/signal - n_idler(idler*1e6)/idler)

def _compute_delta_k(wl1, wl2, n_signal, n_idler, n_pump):
    wl_pump = _compute_pump_wavelength(wl1,wl2)
    return 2*np.pi*(n_pump(wl_pump*1e6)/wl_pump - n_signal(wl1*1e6)/wl1 - n_idler(wl2*1e6)/wl2)

def rect(x, center, width):
    """A rectangular window function.

    Parameters
    ----------
    x : float
        The postion at which to evaluate the window function.
    center : float
        The center of the window function.
    width : float
        The Width of the window function.

    Returns
    -------
    float
        The value of the window function at position x.
    """
    return np.heaviside(x-center+width/2,1)-np.heaviside(x-center-width/2,1)

class Experiment():
    """The experiment class incorporates the tools for computing the PMF, JSA, Schmidt decomposition and heralding efficiencies.
    
    Parameters
    ----------
    waveguide : pyjsa.waveguide.Waveguide
        A waveguide object for the experiment.
    pump : pyjsa.pump.Pump
        A pump object for the experiment.
    signal : tuple
        A tuple where the first element is the wavelength of the signal and the second is the width of the window (meters).
    idler : tuple
        A tuple where the first element is the wavelength of the idler and the second is the width of the window (meters).
    SPDC_type: int, Optional
        The type of the SPDC process. Can only be 0, 1 or 2, by default 0.
    """
    
    def __init__(self, waveguide:Waveguide, pump:Pump, signal, idler, SPDC_type = 0) -> None:
        self._waveguide = waveguide
        self._pump = pump
        self._pmf = None
        self._poling_period = None
        self._delta_k = None
        
        self._pump.signal = signal
        self._pump.idler = idler
        
        self._SPDC_type = SPDC_type
        
    @property
    def pump(self):
        """pyjsa.pump.Pump: The pump in the experiment.
        """
        return self._pump
    
    @pump.setter
    def pump(self, this_pump):
        self._pump = this_pump
        
    @property
    def waveguide(self):
        """pyjsa.waveguide.Waveguide: The waveguide in the experiment.
        """
        return self._waveguide
    
    @waveguide.setter
    def waveguide(self, this_waveguide):
        self._waveguide = this_waveguide
    
    @property
    def pmf(self):
        """numpy.ndarray: The PMF. If it is None, it will be computed.
        """
        if type(self._pmf) == type(None):
            print("PMF is not computed! Computing PMF...")
            self._pmf = self.phase_matching_function()
        return self._pmf
    
    @pmf.setter
    def pmf(self, this_pmf):
        self._pmf = this_pmf
    
    @property
    def poling_period(self):
        """float: The poling period for the specified process, signal and idler combination. Cannot be set.
        """
        if type(self._poling_period) == type(None):
            if self.SPDC_type == 0:
                self._poling_period = _compute_poling_period(self._pump.signal[0], self._pump.idler[0], 
                                                            self._waveguide.neff_TE, self._waveguide.neff_TE, self._waveguide.neff_TE)
            if self.SPDC_type == 1:
                self._poling_period = _compute_poling_period(self._pump.signal[0], self._pump.idler[0], 
                                                   self._waveguide.neff_TM, self._waveguide.neff_TE, self._waveguide.neff_TE)
            if self.SPDC_type == 2:
                self._poling_period = _compute_poling_period(self._pump.signal[0], self._pump.idler[0], 
                                                   self._waveguide.neff_TM, self._waveguide.neff_TE, self._waveguide.neff_TM)
        return self._poling_period
    
    @property
    def delta_k(self):
        """numpy.ndarray: The phase mismatch along the :math:`\lambda_i-\lambda_s` plane. Cannot be set.
        """
        if type(self._delta_k) == type(None):
            _signal_range, _idler_range = np.meshgrid(*self.pump.signal_idler_ranges())
            if self.SPDC_type == 0:
                self._delta_k = _compute_delta_k(_signal_range, _idler_range, self._waveguide.neff_TE, self._waveguide.neff_TE, self._waveguide.neff_TE)
            if self.SPDC_type == 1:
                self._delta_k = _compute_delta_k(_signal_range, _idler_range, self._waveguide.neff_TM, self._waveguide.neff_TE, self._waveguide.neff_TE)
            if self.SPDC_type == 2:
                self._delta_k = _compute_delta_k(_signal_range, _idler_range, self._waveguide.neff_TM, self._waveguide.neff_TE, self._waveguide.neff_TM)
        return self._delta_k
    
    @property
    def SPDC_type(self):
        """int: The SPDC type.
        """
        return self._SPDC_type
    
    @SPDC_type.setter
    def SPDC_type(self, this_SPDC_type):
        self._SPDC_type = this_SPDC_type
        
    def phase_matching_function(self, points = 10000):
        """A function that computed the PMF for the specified signal, idler ranges and waveguide poling profile.

        Parameters
        ----------
        points : int, optional
            The number of points into which to discretize the length of the waveguide if its profile is set to CUSTOM, by default 10000

        Returns
        -------
        numpy.ndarray
            The PMF.
        """
        if self.waveguide.profile == Waveguide.GAUSSIAN_POLED:
            PMF = np.zeros((self.pump.points, self.pump.points), dtype=np.complex64)
            _dz = self.poling_period/2
            _w = np.exp(1j*(self.delta_k)*_dz)
            _factor = 1
            for gm in tqdm(self.waveguide.g(self.poling_period)):
                PMF += gm*_factor
                _factor = _factor*_w
                
            PMF = PMF/(1j*self.delta_k)*(np.exp(1j*self.delta_k*_dz)-1)
            
        elif self.waveguide.profile == Waveguide.REGULAR_POLED:
            dk = self.delta_k - 2*np.pi/self.poling_period
            PMF = 1/(1j*dk)*(np.exp(1j*dk*self.waveguide.length)-1)
                
        elif self.waveguide.profile == Waveguide.CUSTOM_POLED:
            PMF = np.zeros((self.pump.points, self.pump.points), dtype=np.complex64)
            _dz = self.poling_period/2
            _w = np.exp(1j*(self.delta_k)*_dz)
            _factor = 1
            for gm in tqdm(self.waveguide.g(self.poling_period)):
                PMF += gm*_factor
                _factor = _factor*_w
                
            PMF = PMF/(1j*self.delta_k)*(np.exp(1j*self.delta_k*_dz)-1)
            
        elif self.waveguide.profile == Waveguide.GAUSSIAN:
            print("Computing integrated pmf")
            PMF = _gaussian_pmf(self.waveguide.length, self.delta_k, self.waveguide.length/4, self.poling_period)
            
        elif self.waveguide.profile == Waveguide.CUSTOM:
            print("second pmf")
            _z, _dz = np.linspace(0, self._waveguide.length, points, retstep=True, endpoint=False)
            PMF = np.zeros((self.pump.points, self.pump.points), dtype=np.complex64)

            _w = np.exp(1j*(self.delta_k-2*np.pi/self.poling_period)*_dz)
            _factor = 1
            
            for pos in range(len(_z)):
                PMF += self.waveguide.g(poling_period=self.poling_period)(_z[pos])*_factor
                _factor = _factor*_w
            
            PMF = PMF*_dz*_w**(1/2)*np.sinc((self.delta_k-2*np.pi/self.poling_period)*_dz/2)
        
        return PMF

    def joint_spectral_amplitude(self, filter_signal_width, filter_idler_width, filter_signal_center, filter_idler_center):
        """A function that computes the JSA for the specified waveguide, pump and signal and idler ranges combination, incorporating filtering, For no filtering, you should set the center and width of the filters to those of the signal and idler 

        Parameters
        ----------
        filter_signal_width : float 
            The width of the filter on the signal.
        filter_idler_width : float
            The width of the filter on the idelr
        filter_signal_center : float
            The center of the filter on the signal.
        filter_idler_center : float
            The center of the filter on the idler.

        Returns
        -------
        numpy.ndarray
            The JSA.
        float
            Probability that the signal passes its filter.
        float
            Probability that the idler passes its filter.
        float:
            Probability that both the signal and the idler pass their filters.
        """
        _signal_range, _idler_range = self.pump.signal_idler_ranges()
        _filter_signal = rect(_signal_range, filter_signal_center, filter_signal_width)
        _filter_idler = rect(_idler_range, filter_idler_center, filter_idler_width)
        _filter_idler, _filter_signal = np.meshgrid(_filter_idler, _filter_signal)
        _filter = _filter_signal*_filter_idler
        _signal_grad, _idler_grad = np.meshgrid(np.gradient(_signal_range), np.gradient(_idler_range))
        _pump_spectrum = self.pump.pump_envelope_function()
        jsa = self.pmf*_pump_spectrum
        _norm = np.sqrt(np.sum(np.abs(jsa)**2))
        jsa /= _norm
        p_signal_passes = np.sum(_signal_grad*_idler_grad*np.abs(jsa)**2*np.abs(_filter_signal)**2)
        p_idler_passes = np.sum(_signal_grad*_idler_grad*np.abs(jsa)**2*np.abs(_filter_idler)**2)
        p_both_pass = np.sum(_signal_grad*_idler_grad*np.abs(jsa)**2*np.abs(_filter))
        return jsa*_filter, p_signal_passes, p_idler_passes, p_both_pass

    def schmidt_decomposition(self, filter_signal_width, filter_idler_width, filter_signal_center, filter_idler_center):
        """A function that computes the Schmidt decomposition of the JSA.

        Parameters
        ----------
        filter_signal_width : float 
            The width of the filter on the signal.
        filter_idler_width : float
            The width of the filter on the idelr
        filter_signal_center : float
            The center of the filter on the signal.
        filter_idler_center : float
            The center of the filter on the idler.

        Returns
        -------
        numpy.ndarray
            An array of the normalized singular values of the JSA.
        float
            The spectral purity of the output photons.
        """
        _jsa, _, _, _ = self.joint_spectral_amplitude(filter_signal_width, filter_idler_width, filter_signal_center, filter_idler_center)
        U, _values, V = np.linalg.svd(_jsa)
        _values = _values/np.sqrt(np.sum(_values**2))
        _purity = np.sum(_values**4)
        return _values, _purity

def find_optimal_pump_width(exp:Experiment, width_bounds, filter_signal_width, filter_idler_width, filter_signal_center, filter_idler_center):
    """A function that optimizes the width of the pump of an experiment such that it yields the highest spectral purity. It uses the default optimizer of scipy.optimize.minimize_scalar.

    Parameters
    ----------
    exp : Experiment
        The experiment whose pump width is to be optimized.
    width_bounds : numpy.array, tuple
        An array with two elements that specifies the bounds of the optimization, ex. [0.1, 10] (nanometers).
    filter_signal_width : float 
        The width of the filter on the signal.
    filter_idler_width : float
        The width of the filter on the idelr
    filter_signal_center : float
        The center of the filter on the signal.
    filter_idler_center : float
        The center of the filter on the idler.

    Returns
    -------
    scipy.optimize.OptimizeResult
        The result of the optimization routine.
    """
    
    def _impurity(w):
        exp.pump.width = w*1e-9
        _, purity = exp.schmidt_decomposition(filter_signal_width, filter_idler_width, filter_signal_center, filter_idler_center)
        return 1-purity
    
    res = minimize_scalar(_impurity, method="bounded", bounds=width_bounds)
    return res

        