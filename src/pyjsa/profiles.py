from sqlite_utils import Database
import json
import numpy as np
from scipy.interpolate import interp1d

class Profile():
    def __init__(self, data: dict = dict()) -> None:
        self._db = Database("profiles.db")
        self.table = None
        self._data = data
        self.pk = None
        
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value: dict):
        self._data = value
                       
    def save(self):
        if self.data != None and self.table != None and self.pk != None:
            self._db[self.table].upsert(self.data, pk=self.pk)
        elif self.data == None:
            raise Exception("Profile data is null!")
        elif self.type == None:
            raise Exception("Process type not specified!")
        
    def load(self, pk: any):
        self.data = self._db[self.table].get(pk)
        
class DispersionProfile(Profile):
    def __init__(self, data: dict = dict()) -> None:
        super().__init__(data)
        self.table = "dispersion"
        self.pk = ["type", "filmThickness", "width", "height", "cladding", "material", "substrate", "temperature"]
        
    @property
    def type(self):
        return self.data["type"]
    
    @type.setter
    def type(self, value: str):
        self.data["type"] = value
        
    @property
    def filmThickness(self):
        return self.data["filmThickness"]
    
    @filmThickness.setter
    def filmThickness(self, value: float):
        self.data["filmThickness"] = value
        
    @property
    def width(self):
        return self.data["width"]
    
    @width.setter
    def width(self, value: float):
        self.data["width"] = value
        
    @property
    def height(self):
        return self.data["height"]
    
    @height.setter
    def height(self, value: float):
        self.data["height"] = value
        
    @property
    def cladding(self):
        return self.data["cladding"]
    
    @cladding.setter
    def cladding(self, value: str):
        self.data["cladding"] = value
        
    @property
    def material(self):
        return self.data["material"]
    
    @material.setter
    def material(self, value: str):
        self.data["material"] = value
        
    @property
    def substrate(self):
        return self.data["substrate"]
    
    @substrate.setter
    def substrate(self, value: str):
        self.data["substrate"] = value
        
    @property
    def temperature(self):
        return self.data["temperature"]
    
    @temperature.setter
    def temperature(self, value: str):
        self.data["temperature"] = value
        
    @property
    def wavelengths(self):
        return np.array(json.loads(self.data["wavelengths"]))
    
    @wavelengths.setter
    def wavelengths(self, value: np.ndarray):
        self.data["wavelengths"] = json.dumps(list(value))
        
    @property
    def neffsTE(self):
        return np.array(json.loads(self.data["neffsTE"]))
    
    @neffsTE.setter
    def neffsTE(self, value: np.ndarray):
        self.data["neffsTE"] = json.dumps(list(value))
        
    @property
    def neffsTM(self):
        return np.array(json.loads(self.data["neffsTM"]))
    
    @neffsTE.setter
    def neffsTE(self, value: np.ndarray):
        self.data["neffsTM"] = json.dumps(list(value))
        
    def neffs(self, pol: str):
        #assert pol in ['TE', 'TM']
        if pol == 'TE': return interp1d(self.wavelengths, self.neffsTE, bounds_error=False, fill_value="extrapolate", kind = "linear")
        if pol == 'TM': return interp1d(self.wavelengths, self.neffsTM, bounds_error=False, fill_value="extrapolate", kind = "linear")    
        
class SetupProfile(Profile):
    def __init__(self, data: dict = dict()) -> None:
        super().__init__(data)
        self.table = "setup"
        self.pk = "name"
    
    @property
    def name(self):
        return self.data["name"]
    
    @name.setter
    def name(self, value: str):
        self.data["name"] = value
    
    @property
    def pumpCenter(self):
        return self.data["pumpCenter"]
    
    @pumpCenter.setter
    def pumpCenter(self, value: float):
        self.data["pumpCenter"] = value
        
    @property
    def pumpBandwidth(self):
        return self.data["pumpBandwidth"]
    
    @pumpBandwidth.setter
    def pumpBandwidth(self, value: float):
        self.data["pumpBandwidth"] = value
        
    @property
    def pumpType(self):
        return self.data["pumpType"]
    
    @pumpType.setter
    def pumpType(self, value: str):
        self.data["pumpType"] = value
        
    @property
    def pumpPol(self):
        return self.data["pumpPol"]
    
    @pumpPol.setter
    def pumpPol(self, value: str):
        #assert value in ['TE', 'TM']
        self.data["pumpPol"] = value
        
    @property
    def signalCenter(self):
        return self.data["signalCenter"]
    
    @signalCenter.setter
    def signalCenter(self, value: float):
        self.data["signalCenter"] = value
        
    @property
    def signalWidth(self):
        return self.data["signalWidth"]
    
    @signalWidth.setter
    def signalWidth(self, value: float):
        self.data["signalWidth"] = value
        
    @property
    def signalPol(self):
        return self.data["signalPol"]
    
    @signalPol.setter
    def signalPol(self, value: str):
        #assert value in ['TE', 'TM']
        self.data["signalPol"] = value
        
    @property
    def idlerCenter(self):
        return self.data["idlerCenter"]
    
    @idlerCenter.setter
    def idlerCenter(self, value: float):
        self.data["idlerCenter"] = value
        
    @property
    def idlerWidth(self):
        return self.data["idlerWidth"]
    
    @idlerWidth.setter
    def idlerWidth(self, value: float):
        self.data["idlerWidth"] = value
        
    @property
    def idlerPol(self):
        return self.data["idlerPol"]
    
    @idlerPol.setter
    def idlerPol(self, value: str):
        #assert value in ['TE', 'TM']
        self.data["idlerPol"] = value
    
    @property
    def signalFilterCenter(self):
        return self.data["signalFilterCenter"]
    
    @signalFilterCenter.setter
    def signalFilterCenter(self, value: float):
        self.data["signalFilterCenter"] = value
        
    @property
    def signalFilterWidth(self):
        return self.data["signalFilterWidth"]
    
    @signalFilterWidth.setter
    def signalFilterWidth(self, value: float):
        self.data["signalFilterWidth"] = value
    
    @property
    def idlerFilterCenter(self):
        return self.data["idlerFilterCenter"]
    
    @idlerFilterCenter.setter
    def idlerFilterCenter(self, value: float):
        self.data["idlerFilterCenter"] = value
        
    @property
    def idlerFilterWidth(self):
        return self.data["idlerFilterWidth"]
    
    @idlerFilterWidth.setter
    def idlerFilterWidth(self, value: float):
        self.data["idlerFilterWidth"] = value
        
    @property
    def dispersion(self):
        profile = DispersionProfile()
        dispersion_keys = list(v for k,v in self.data.items() if k in profile.pk)
        profile.load(dispersion_keys)
        return profile
    
    @dispersion.setter
    def dispersion(self, value: DispersionProfile):
        for k in value.pk:
            self.data[k] = value.data[k]
            
    @property
    def domains(self):
        return np.array(json.loads(self.data["domains"]))
    
    @domains.setter
    def domains(self, value: str):
        self.data["domains"] = json.dumps(list(value))
        
    @property
    def length(self):
        return np.sum(self.domains)
    
    @property
    def orientation(self):
        return np.array(json.loads(self.data["orientation"]))
    
    @orientation.setter
    def orientation(self, value: str):
        self.data["orientation"] = json.dumps(list(value))
        
    def isRegularPoling(self) -> bool:
        domainsEqual = np.all(self.domains == self.domains[0])
        upDownEqual = np.sum(self.orientation) in [-1, 0, 1]
        return domainsEqual and upDownEqual
    
    def getPolingPeriod(self) -> float:
        # in um
        dispersion = self.dispersion
        return 1/(dispersion.neffs(self.pumpPol)(self.pumpCenter*1e-3)/(self.pumpCenter*1e-3)\
            - dispersion.neffs(self.signalPol)(self.signalCenter*1e-3)/(self.signalCenter*1e-3)\
            - dispersion.neffs(self.idlerPol)(self.idlerCenter*1e-3)/(self.idlerCenter*1e-3))
        
    def wavelengthRanges(self, points: list):
        signalGrid, idlerGrid = np.meshgrid(
            np.linspace(self.signalCenter-self.signalWidth/2, 
                        self.signalCenter+self.signalWidth/2, points[0]),
            np.linspace(self.idlerCenter-self.idlerWidth/2, 
                        self.idlerCenter+self.idlerWidth/2, points[1])
        )
        pumpGrid = 1/(1/signalGrid + 1/idlerGrid)
        return signalGrid, idlerGrid, pumpGrid
    
    def dk(self, points: list):
        signalGrid, idlerGrid, pumpGrid = self.wavelengthRanges(points)
        signalGrid, idlerGrid, pumpGrid = signalGrid*1e-3, idlerGrid*1e-3, pumpGrid*1e-3
        return 2*np.pi*(self.dispersion.neffs(self.pumpPol)(pumpGrid)/(pumpGrid)\
            - self.dispersion.neffs(self.signalPol)(signalGrid)/(signalGrid) - \
                self.dispersion.neffs(self.idlerPol)(idlerGrid)/(idlerGrid))
        
    
class PyJSATable():
    def __init__(self, table: str) -> None:
        self._db = Database("profiles.db")
        self.table = table
        
    @property
    def count(self):
        return self._db[self.table].count
        
    def get_column(self, column: str):
        values = self._db.query(f"SELECT {column} FROM {self.table}")
        return [val[column] for val in values]
    
    def get_unique_column(self, column: str):
        values = self._db.query(f"SELECT DISTINCT {column} FROM {self.table}")
        return [val[column] for val in values]
    
    def delete(self, name: str):
        self._db[self.table].delete(name)
        
    def get(self, pk: str or tuple):
        return self._db[self.table].get(pk)