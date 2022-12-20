"""The Pump package contains only the class Pump, used to compute and store the properties of the pump laser. 
"""

import numpy as np
from scipy.special import hermite

class Pump():
    """A class for storing and computing the properties of the pump laser.
    
    Parameters
    ----------
    width : float
        Width of the pump spectrum at half maximum (meters).
    points : int, Optional
        The number of points into which to divide the :math:`\\lambda_i` and :math:`\\lambda_s` axis in order to compute the PEF, by default 1000.
    """
    def __init__(self, width, points = 1000) -> None:
        self._signal = None
        self._idler = None

        self._points = points
        self._width = width / (2 * np.sqrt(np.log(2)))
        
        self._center = None
        
    @property
    def points(self):
        """int: The number of points into which to divide the :math:`\\lambda_i` and :math:`\\lambda_s` axis.
        """
        return self._points
    
    @points.setter
    def points(self, this_points):
        self._points = this_points
    
    @property
    def signal(self):
        """numpy.ndarray: An array with two elements that defines the signal. The first element is the central wavelength and the second is the width of the window (meters).
        """
        return self._signal
    
    @signal.setter
    def signal(self, this_signal):
        self._signal = this_signal
        
    @property
    def idler(self):
        """numpy.ndarray: An array with two elements that defines the idler. The first element is the central wavelength and the second is the width of the window (meters).
        """
        return self._idler
    
    @idler.setter
    def idler(self, this_idler):
        self._idler = this_idler
        
    @property
    def center(self):
        """float: The center of the pump spectrum, inferred from the signal and the idler by energy conservation (meters). Cannot be set.
        """
        if self._center == None:
            self._center = 1/(1/self.signal[0]+1/self.idler[0])
        return self._center
        
    @property
    def width(self):
        """float: The width of the pump spectrum at half maximum (meters).
        """
        return self._width
    
    @width.setter
    def width(self, this_width):
        self._width = this_width / (2 * np.sqrt(np.log(2)))
        
    def signal_idler_ranges(self):
        """A function that returns the signal and idler ranges over which to compute the PEF.

        Returns
        -------
        tuple:
            A tuple where the first elements is the signal range and the second is idler range.
        """
        return np.linspace(self.signal[0]-self.signal[1]/2, self.signal[0]+self.signal[1]/2, self.points), np.linspace(self.idler[0]-self.idler[1]/2, self.idler[0]+self.idler[1]/2, self.points)
        
    def hermite_mode(self, x: float):
        r"""A normalised Hermite-Gaussian function in temporal mode 0:
        
        .. math::

            \frac{e^{-(x_0-x)^2/(2w^2)}}{\sqrt{\sqrt{\pi}w}}H_0(x_0-x)
            
        where :math:`x_0` is the center and :math:`w` is the width.
        
        Parameters
        ----------
        x : float
            The wavelength (meters).
            
        Returns
        -------
        float 
        """
        # On 22.11.2017, Matteo changed all the self.pump_width to self.__correct_pump_width
        # _result = hermite(self.pump_temporal_mode)((self.pump_center - x) /
        #                                            self.pump_width) *    \
        #     exp(-(self.pump_center - x)**2 / (2 * self.pump_width**2)) /\
        #     sqrt(factorial(self.pump_temporal_mode) * sqrt(pi) *
        #          2**self.pump_temporal_mode * self.pump_width)
        # TODO: Check the correctness of the __correct_pump_width parameter
        _result = hermite(0)(self.center - x)* \
                np.exp(-(self.center - x) ** 2 / (2 * self.width ** 2)) / \
                np.sqrt(np.sqrt(np.pi) * self.width)
        return _result

    def pump_envelope_function(self):
        """A function that computes the PEF.

        Returns
        -------
        np.ndarray
            The PEF as a matrix array with dimesnions (points, points).
        """
        _signal_range, _idler_range = np.meshgrid(*self.signal_idler_ranges())
        _wavelenth_range = 1/(1/_signal_range+1/_idler_range)
        return self.hermite_mode(_wavelenth_range)