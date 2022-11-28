#%% Imports
from get_corr_function import *
from get_values import *
from ipy_config import *
from plot_func import *
from power_law_fit import *
from scan import *
from Simulation import *
ipy_config()

#%% Generate 2 simulations
sim1 = Simulation(L = 100, xi = float('inf'), beta = 0.8)
sim1.generate_fields(s_centered = True, s_normalized= True)
sim1.generate_sigmaY(p = 0.1)

sim2 = Simulation(L = 1000, xi = float('inf'), beta = 0.9)
sim2.generate_fields(s_centered = True, s_normalized= True)
sim2.generate_sigmaY(p = 0.1)
# %%
sim1.show_plots()
plt.savefig(f'examples/gen1.png')
sim2.show_plots()
plt.savefig(f'examples/gen2.png')

#%%
sim1.show_final()
plt.savefig(f'examples/fin1.png')
sim2.show_final()
plt.savefig(f'examples/fin2.png')
# %%