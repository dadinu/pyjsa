import os
from sqlite_utils import Database
import numpy as np
import json

db = Database("profiles.db")
"""db.query("DROP TABLE IF EXISTS dispersion")
db["dispersion"].create({
    "type": str,
    "filmThickness": float,
    "width": float,
    "height": float,
    "cladding": str,
    "material": str,
    "substrate": str,
    "temperature": float,
    "wavelengths": str,
    "neffsTE": str,
    "neffsTM": str 
}, pk=("type", "filmThickness", "width", "height", "cladding", "material", "substrate", "temperature"))"""

cut = 'X'
wg_angle = 60
temperature = 20.

film_thicknesses_um = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
cladding = "sio2"
for film_thickness_um in film_thicknesses_um:
    path_to_data_TE = f'\\data\\' \
                        f'LNOI_Neff_Library_{cut}_cut_' \
                        f'film_thickness_{film_thickness_um:.1f}_' \
                        f'cladding_{cladding}_' \
                        f'angle_{wg_angle}_' \
                        f'TE.npz'
    path_to_data_TE = os.path.abspath(os.path.dirname(__file__))+path_to_data_TE

    path_to_data_TM = f'\\data\\' \
                        f'LNOI_Neff_Library_{cut}_cut_' \
                        f'film_thickness_{film_thickness_um:.1f}_' \
                        f'cladding_{cladding}_' \
                        f'angle_{wg_angle}_' \
                        f'TM.npz'
    path_to_data_TM = os.path.abspath(os.path.dirname(__file__))+path_to_data_TM

    library_TE = np.load(path_to_data_TE)
    library_TM = np.load(path_to_data_TM)
    widths = library_TE["wg_width_range"]
    heights = library_TE["wg_height_range"]
    wavelengths = list(library_TE["wavelength_range"])
    
    for idx1, width in enumerate(widths):
        for idx2, height in enumerate(heights):
            if film_thickness_um != np.around(height, 1):
                print(f"Film thickness: {film_thickness_um}; width: {width}; height: {height}")
                data = {
                    "type": "ridge60",
                    "filmThickness": film_thickness_um,
                    "width": np.around(width, 1),
                    "height": np.around(height, 1),
                    "cladding": "SiO2",
                    "material": "LiNbO3X",
                    "substrate": "SiO2",
                    "temperature": temperature,
                    "wavelengths": json.dumps(wavelengths),
                    "neffsTE": json.dumps(list(np.real(np.squeeze(library_TE["LNOI_neffs"][0,0,0,idx2, idx1])))),
                    "neffsTM": json.dumps(list(np.real(np.squeeze(library_TM["LNOI_neffs"][0,0,0,idx2, idx1]))))
                }
                db["dispersion"].upsert(data, pk=("type", "filmThickness", "width", "height", "cladding", "material", "substrate", "temperature"))