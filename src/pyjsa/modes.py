import numpy as np
import matplotlib.pyplot as plt
import opticalmaterialspy as mat
import modesolverpy.mode_solver as ms
import modesolverpy.structure as st
import time

if __name__ == "__main__":
    wl = 1.55
    x_step = 0.015
    y_step = 0.015
    wg_height = 0.3
    wg_width = 1.5
    sub_height = 1.0
    sub_width = 4.
    clad_height = 1.0
    film_thickness = 0.5
    angle = 60.

    n_sub = mat.SiO2().n(wl)
    n_wg_xx = mat.LnAni(cut='x').xx.n(wl)
    n_wg_yy = mat.LnAni(cut='x').yy.n(wl)
    n_wg_zz = mat.LnAni(cut='x').zz.n(wl)
    n_clad = mat.Air().n()
    
    structure = st.RidgeWaveguide(wl, x_step, y_step, wg_height, wg_width,
                                sub_height, sub_width, clad_height,
                                n_sub, n_wg_yy, angle, n_clad, film_thickness)
    
    t0 = time.time()
    solver = ms.ModeSolverSemiVectorial(1, semi_vectorial_method="Ey")
    solver.solve(structure)
    t1 = time.time()
    print(t1-t0)
    plt.pcolormesh(solver.modes[0])
    plt.show()