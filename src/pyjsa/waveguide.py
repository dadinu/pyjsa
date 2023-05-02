"""The Waveguide package, containing tools for manipulating and and constructing waveguide geometry and physical data. 
"""

import numpy as np
from scipy.special import erf
from scipy.interpolate import interp1d
import os

def pmf_gaussian(z, L):
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

def find_poling_profile(length, poling_period, target_pmf, *args):
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

"""def find_poling_profile_subdomain(length, poling_period, domain_ratio, field_func, *args):
    _domains = 2*int(length/poling_period)
    _poling_profile = np.ones(domain_ratio*_domains)
    _poling_period = poling_period
    _next = 0
    for i in range(domain_ratio*_domains):
        _target_next = field_func((i+1)*_poling_period/2/domain_ratio, *args)
        _next_up = _next + 1/(1j*2*np.pi/_poling_period)*(np.exp(1j*np.pi/domain_ratio)-1)*np.exp(1j*i*np.pi/domain_ratio)
        _next_down = _next - 1/(1j*2*np.pi/_poling_period)*(np.exp(1j*np.pi/domain_ratio)-1)*np.exp(1j*i*np.pi/domain_ratio)
        _e_up = np.abs(_target_next - _next_up)
        _e_down = np.abs(_target_next - _next_down)
        if _e_up < _e_down:
            _poling_profile[i] = 1
            _next = _next_up
        elif _e_down <= _e_up:
            _poling_profile[i] = -1
            _next = _next_down
    return _poling_profile"""

class Waveguide():
    """Implements a Waveguide object, which stores information relevant for the LNOI waveguide construction and material properties. The properties of the waveguide like the dispersion relation are stored externally in .npz files in the folder "..\\data\\".

    Attributes
    ----------
    GAUSSIAN_POLED : int
        Attribute for specifying that the waveguide has a Gaussian poling profile.
    GAUSSIAN : int
        Attribute for specifying that the waveguide has a Gaussian nonlinearity profile.
    REGULAR_POLED : int
        Attribute for specifying that the waveguide has a regular poling profile.
    CUSTOM_POLED : int
        Attribute for specifying that the waveguide has a custom poling profile.
    CUSTOM : int
        Attribute for specifying that the waveguide has a custom nonlinearity profile.  
        
    Parameters
    ----------
    film_thickness_um : float
        Thickness of the LN film used in the fabrication of the waveguide. For the default dataset, values can only be elements of the array [0.3:0.1:0.8] (micrometers).
    width_idx : int
        The width of the waveguide. It specifies the index of the element in the (default) array [0.5:0.1:2.0] (micrometers).
    height_idx : int
        The height of the waveguide. It specifies the index of the element in the (default) array [0.2:0.1:film_thickness] (micrometers).
    length : float
        The length of the waveguide (meters).
    wg_angle : float, Optional
        The angle of the waveguide ridge (degrees). For the default dataset, only the default value of 60 is possible.
    cladding : string, Optional
        The cladding of the waveguide. For the default dataset, only the default value of "air" is possible.
    profile : int, Optional
        An integer specifying the poling of the waveguide taken from the attributes of the class mentioned above, by default 0. 
    custom_poling_profile : numpy.ndaray, Optional
        A custom poling profile to be used if the waveguide is specified to be CUSTOM_POLED, by default None.
    custom_nonlinearity_profile : callable, Optional
        A custom nonlinearity profile to be used if the waveguide is specified to be CUSTOM, by default None.
    """

    GAUSSIAN_POLED = 0
    GAUSSIAN = 1
    REGULAR_POLED = 2
    CUSTOM = 3
    CUSTOM_POLED = 4

    def __init__(self, 
                 film_thickness_um: float, 
                 width_idx: int, 
                 height_idx: int, 
                 length: float, 
                 wg_angle = 60, 
                 cladding = "air", 
                 profile = 0,
                 custom_poling_profile = None,
                 custom_nonlinearity_profile = None) -> None:
        
        
        # Fixed parameters not available in library
        self.cut = 'X'
        self.wg_angle = wg_angle
        self.temperature = 20
        
        self.film_thickness_um = film_thickness_um
        self.cladding = cladding.lower()
        if self.cladding == 'sio2':
            self.cladding = 'glass'
        
        path_to_data_TE = f'\\data\\' \
                         f'LNOI_Neff_Library_{self.cut}_cut_' \
                         f'film_thickness_{film_thickness_um:.1f}_' \
                         f'cladding_{self.cladding}_' \
                         f'angle_{self.wg_angle}_' \
                         f'TE.npz'
        path_to_data_TE = os.path.abspath(os.path.dirname(__file__))+path_to_data_TE
        
        path_to_data_TM = f'\\data\\' \
                         f'LNOI_Neff_Library_{self.cut}_cut_' \
                         f'film_thickness_{film_thickness_um:.1f}_' \
                         f'cladding_{self.cladding}_' \
                         f'angle_{self.wg_angle}_' \
                         f'TM.npz'
        path_to_data_TM = os.path.abspath(os.path.dirname(__file__))+path_to_data_TM
            
        self._library_TE = np.load(path_to_data_TE)
        self._wg_height_range = self._library_TE['wg_height_range']
        self._wg_width_range = self._library_TE['wg_width_range']
        self._wavelengths = self._library_TE['wavelength_range']
        self._LNOI_neffs_TE = self._library_TE['LNOI_neffs']
        
        self._library_TM = np.load(path_to_data_TM)
        self._LNOI_neffs_TM = self._library_TM['LNOI_neffs']
        
        self._wg_angle_idx = 0
        self._polarization_idx = 0
        self._cut_idx = 0
        
        self._profile = profile

        self._length = length
        self._custom_poling_profile = custom_poling_profile
        self._custom_nonlinearity_profile = custom_nonlinearity_profile

        #load the wavelengths and effective indices and check for NaNs
        wls_TE = wls_TM = self._wavelengths
        
        self._neff_TE = np.real(np.squeeze(self._LNOI_neffs_TE[self._cut_idx,
                                    self._polarization_idx,
                                    self._wg_angle_idx,
                                    height_idx,
                                    width_idx]))
        mask_TE = np.isnan(self._neff_TE)
        wls_TE = wls_TE[~mask_TE]
        self._neff_TE = self._neff_TE[~mask_TE]
        
        self._neff_TM = np.real(np.squeeze(self._LNOI_neffs_TM[self._cut_idx,
                                    self._polarization_idx,
                                    self._wg_angle_idx,
                                    height_idx,
                                    width_idx]))
        mask_TM = np.isnan(self._neff_TM)
        wls_TM = wls_TM[~mask_TM]
        self._neff_TM = self._neff_TM[~mask_TM]
        

        self._neff_TE = interp1d(wls_TE, self._neff_TE, bounds_error=False, fill_value="extrapolate", kind = "linear")
        self._neff_TM = interp1d(wls_TM, self._neff_TM, bounds_error=False, fill_value="extrapolate", kind = "linear")
        
    #TODO: remove neff properties
    @property
    def neff_TE(self):
        """callable: Dispersion relation for TE polarization, of the form neff_TE(wavelength in micrometers).
        """
        return self._neff_TE

    @property
    def neff_TM(self):
        """callable: Dispersion relation for TM polarization, of the form neff_TM(wavelength in micrometers).
        """
        return self._neff_TM

    @property
    def length(self):
        """float: Length of the waveguide. 
        """
        return self._length
    
    @length.setter
    def length(self, value):
        self._length = value
    
    @property
    def profile(self):
        """int: Profile of the waveguide.
        """
        return self._profile
    
    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def custom_poling_profile(self):
        """np.ndarray: A custom poling profile for the waveguide.
        """
        return self._custom_poling_profile
    
    @custom_poling_profile.setter
    def custom_poling_profile(self, value):
        self._custom_poling_profile = value
        
    @property
    def custom_nonlinearity_profile(self):
        """callable: A custom nonlinearity profile for the waveguide.
        """
        return self._custom_nonlinearity_profile
    
    @custom_nonlinearity_profile.setter
    def custom_nonlinearity_profile(self, value):
        self._custom_nonlinearity_profile = value        

    def n_eff(self, pol: str):
        assert pol in ["TE", "TM"]
        if pol == "TE":
            return self._neff_TE
        if pol == "TM":
            return self._neff_TM
    
    def g(self, poling_period = None):
        """A function that returns the poling profile or nonlinearity profile of the waveguide, depending on the profile attribute of the class.

        Parameters
        ----------
        poling_period : float, optional
            The poling period of the waveguide (meters), by default None.

        Returns
        -------
        np.ndarray or callable
            The poling profile or nonlinearity profile of the waveguide.
        """
        if self.profile == self.GAUSSIAN:
            return lambda z: np.exp(-16*(z - self._length / 2.) ** 2 / (2 * (self._length) ** 2))
        elif self.profile == self.REGULAR_POLED:
            _profile = np.empty((int(2*self.length/poling_period-1),))
            _profile[::2] = 1
            _profile[1::2] = -1
            return _profile
        elif self.profile == self.GAUSSIAN_POLED:
            return find_poling_profile(self.length, poling_period, pmf_gaussian, self.length)
        elif self.profile == self.CUSTOM:
            return lambda z: self.custom_nonlinearity_profile(z)
        elif self.profile == self.CUSTOM_POLED:
            return self.custom_poling_profile
            


        


