#%% Imports
import numpy as np
import matplotlib.pyplot as plt
from Simulation import *
import pandas as pd
import h5py
from scan import *

from IPython import get_ipython
ipython = get_ipython()
ipython.run_line_magic("matplotlib", "qt")
ipython.run_line_magic("load_ext", "autoreload")
ipython.run_line_magic("autoreload", "2")

#%% Generate
p = 0.1
beta_list = [0.6, 0.7, 0.8]
xi_list = [10, 100, 1e8]
L = 1000

sims = scan(L_list = [L], beta_list = beta_list, xi_list = xi_list)

for sim in sims:
    sim.generate_sigmaY(p)


#%% Show s and sigmay
sims[5].show_final()

# %% Export result as matrix (dataset)
f = h5py.File('data.hdf5','w')
group = f.create_group('sigmaY')
group.create_dataset('xx', data = sim.get_coordinates())
group.create_dataset('yy', data = sim.get_coordinates())
for sim in sims:
    group.create_dataset(f'L={L}beta={sim.beta:}xi={sim.xi}p={p}', data = sim.sigmaY)

f.close()

# #%% Export result as CSV (here there was a shift in coordinates but whatever)
# xx, yy = sim.get_coordinates()
# sigmaY = sim.sigmaY
# stack = np.stack([xx,yy,sigmaY])
# flat = stack.reshape(3,-1)
# df = pd.DataFrame(flat.T, columns = ['x','y','sigmaY'])

# df.to_csv('sigmaY', index = False)
# %%
