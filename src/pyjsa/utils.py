import numpy as np
from scipy.special import erf, hermite

def hermiteMode(x: float, width: float, center: float):
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
        _result = hermite(0)(center - x)* \
                np.exp(-(center - x) ** 2 / (2 * width ** 2)) / \
                np.sqrt(np.sqrt(np.pi) * width)
        return _result

def pmfGaussian(z, L):
    """A function to compute the PMF for a waveguide with a Gaussian nonlinearity profile at a fixed phase mismatch 

    Parameters
    ----------
    z : float
        position along the waveguide
    L : float
        length of the waveguide

    Returns
    -------
    float
        PMF at the specified position
    """
    return -2/np.pi*np.sqrt(np.pi/2)*L/4*(erf((L-2*z)/2/np.sqrt(2)/(L/4))-erf(np.sqrt(2)))

def findGaussianProfile(length, poling_period, target_pmf, *args):
    """An implementation of the deleted domain algorithm described in Chapter 2.

    Parameters
    ----------
    length : float 
        The length of the waveguide (meters).
    poling_period : float
        The poling period of the waveguide (meters).
    target_pmf : callable
        A function that returns the target PMF at a position along the waveguide.
    args : iterable
        Arguments to be passed to target_pmf 

    Returns
    -------
    np.ndarray
        The poling profile that minimizes the error between the target PMF and the resulting PMF.
    """
    _domains = int(length/poling_period)
    _poling_profile = np.ones(2*_domains)
    _poling_period = poling_period
    _poling_period_pi = _poling_period/np.pi
    _next = 0
    for i in range(_domains):
        _target_next = target_pmf((i+1)*_poling_period, *args)
        e = _target_next - _next
        
        if -_poling_period_pi <= e and e<=_poling_period_pi:
            _poling_profile[2*i] = 1
            _poling_profile[2*i+1] = 1
        elif _poling_period_pi < e:
            _poling_profile[2*i] = 1
            _poling_profile[2*i+1] = -1
        elif e < -_poling_period_pi:
            _poling_profile[2*i] = -1
            _poling_profile[2*i+1] = 1
        _next = _next + (_poling_profile[2*i] - _poling_profile[2*i+1])*_poling_period_pi
    
    return _poling_profile