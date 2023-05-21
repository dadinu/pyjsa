from pyjsa.profiles import SetupProfile
from pyjsa.utils import hermiteMode
import numpy as np
from scipy.linalg import svd
from tqdm import trange

class SPDC():
    def __init__(self, setup: SetupProfile, points: list) -> None:
        self.setup = setup
        self.points = points

    def PEF(self):
        _, _, pumpGrid = self.setup.wavelengthRanges(self.points)
        self.pef = hermiteMode(pumpGrid, self.setup.pumpBandwidth, self.setup.pumpCenter)

    def PMF(self):
        if self.setup.isRegularPoling():
            dk = self.setup.dk(self.points)-2*np.pi/self.setup.getPolingPeriod()
            self.pmf = 1/(1j*dk)*(np.exp(1j*dk*self.setup.length)-1)
        else:
            pmf = np.zeros((self.points[0], self.points[1]), dtype=np.complex64)
            dk = self.setup.dk(self.points)
            dz = self.setup.domains
            dzs = np.cumsum(dz)
            g = self.setup.orientation
            
            iter = trange(len(g))
            for m in iter:
                pmf += g[m]*np.exp(1j*dk*dzs[m])*(1-np.exp(-1j*dk*dz[m]))
            self.pmf = pmf/(1j*dk)

    def JSA(self):
        self.jsa = self.pef*self.pmf
        U, values, V = svd(self.jsa)
        self.values = values/np.sqrt(np.sum(values**2))
        self.purity = np.around(np.sum(self.values**4)*100, 2)