from matplotlib.colors import LogNorm
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as fft
from scipy.optimize import curve_fit
plt.style.use('./modules/config/style.mplstyle')
from matplotlib.animation import FuncAnimation
from sklearn.linear_model import LinearRegression
from matplotlib.widgets import TextBox, Button
from tqdm import tqdm
from linetimer import linetimer
import matplotlib as mpl
import warnings
import pandas as pd


#############IMSHOW CONFIGURATION#################

def plot_map(f:np.ndarray, name:str, centered = False):
    """Plots a map in real space, possibly centered.

    Args:
        f (np.ndarray): Field that should be mapped.
        name (str): Title that should appear.
        centered (bool, optional): Determines whether the origin (0,0) should be set at the center of the image.
        Defaults to False.
    """
    
    if(centered):
        f = fft.fftshift(f)
        L = f.shape[0]
        xlabels = (np.fft.fftfreq(L)*L).astype(int)
        ylabels = xlabels.copy()
        xlabels.sort()
        ylabels.sort()
        
        plt.gca().set_xticks(range(len(xlabels)))
        plt.gca().set_yticks(range(len(ylabels)))
        plt.gca().set_xticklabels(xlabels)
        plt.gca().set_yticklabels(ylabels)
        plt.locator_params(nbins=10)
    
    plt.imshow(f, origin = 'lower')
    plt.colorbar()
    plt.title(name, fontsize = 20)
    plt.xlabel(r'$x$')
    plt.ylabel(r'$y$')
    
def plot_ft(f:np.ndarray, name:str, centered = True, logscale = False):
    """Plots a map (``f``) that is a 2D Fourier transform (of another map), possibly centered and using a logscale colormap.
    
    Args:
        f (np.ndarray): Field that should be mapped.
        name (str): Title that should appear.
        centered (bool, optional): Determines whether the origin (0,0) should be set at the center of the image. 
        Defaults to True.
        logscale (bool, optional): Determines whether a logscale colormap should be used. Defaults to False.
    """
    #prepare frequency grid
    L = f.shape[0]
    qx,qy = np.fft.fftfreq(L), np.fft.fftfreq(L)
    
    #get the labels for frequency axis (centered labels)
    xlabels = qx.ravel().copy()
    ylabels = qy.ravel().copy()
    
    #center if asked
    if(centered):
        f = fft.fftshift(f)
        xlabels.sort()
        ylabels.sort()
    
    #scale of the colormap
    if(logscale):
        plt.imshow(np.abs(f), origin = 'lower', norm = LogNorm())
    else:
        plt.imshow(np.abs(f), origin = 'lower')
        
    plt.colorbar()
    plt.title(name, fontsize = 20)
    #correct frequency axis labels
    plt.gca().set_xticks(range(len(xlabels)))
    plt.gca().set_yticks(range(len(ylabels)))
    plt.gca().set_xticklabels(xlabels)
    plt.gca().set_yticklabels(ylabels)
    plt.locator_params(nbins=10)
    plt.xlabel(r'$q_x$')
    plt.ylabel(r'$q_y$')
    
############POWER LAW FITS#################
    
def regularized_power_law(x:np.ndarray, c:float, a:float, reg_value = 0.0) -> np.ndarray:
    """Power law with negative exponent: :math:`c x^{-a}`. The singularity at the origin is replaced by 0.
    This is necessary, as we are working with Fourier-Transforms, which do not accept 'inf' values in the inputs.


    Args:
        x (np.ndarray): Function input.
        c (float): Multiplicative constant.
        a (float): Exponent.
        reg_value (float): Value to impose at x = 0.


    Returns:
        np.ndarray: Regularized power law of ``x``.
    """
    
    f = c*(1/x)**a
    f[f == float('inf')] = reg_value

    #TODO check what we should impose at 0
    return f

def power_law(x:np.ndarray, c:float, a:float) -> np.ndarray:
    """Power law with negative exponent: :math:`c x^{-a}`.

    Args:
        x (np.ndarray): Function input.
        c (float): Multiplicative constant.
        a (float): Exponent.

    Returns:
        np.ndarray: Power law of ``x``.
    """
    return c*(1/x)**a

def power_law_fit(x:np.ndarray,y:np.ndarray) -> tuple[float,float]:
    """Fits a power law (negative exponent) to ``x`` and ``y`` by linear regression on the log-log plot. 
    Returns the optimal parameters ``c`` and ``a``.

    Args:
        x (np.ndarray): x-axis.
        y (np.ndarray): y-axis.


    Returns:
        float: Multiplicative constant.
        float: Exponent (negative).
    """
    
    #filter out 0 and negative values for which the logarithm can not be taken
    y_filtered = y[(x>0) & (y>0)]
    x_filtered = x[(x>0) & (y>0)]
    
    lx = np.log(x_filtered)
    ly = np.log(y_filtered)
    lin_reg = LinearRegression().fit(lx.reshape(-1,1),ly)
    
    return np.exp(lin_reg.intercept_), -lin_reg.coef_[0]

def plot_power_law_fit(x:np.ndarray, y:np.ndarray, label = "") -> float:
    """Generates a power law fit using ``power_law_fit`` and plots the result.

    Args:
        x (np.ndarray): x-axis.
        y (np.ndarray): y-axis.
        label (str, optional): Label for the plot. Defaults to "".

    Returns:
        float: Exponent (negative).
    """


    
    popt = power_law_fit(x, y)
    plt.scatter(x, y, label = label)
    plt.plot(x, power_law(x, *popt), color = 'k', label = f'|slope| = {popt[1]}')
    plt.gca().set_xscale('log')
    plt.gca().set_yscale('log')
    plt.legend()
    
    return popt[1]


############COMPLEX PLOTS#################
def cplot2(ax:plt.Axes, x:np.ndarray, f:np.ndarray, method = 'real-imag', lognorm = False):
    """Visualization function for a complex function ``f`` of ``x``. Always plots two curves:
    either the real and imaginary part (if ``method`` is 'real-imag') or the norm and the angle (if ``method`` is 'norm-arg').

    Args:
        ax (plt.Axes): Axes object on which we should plot.
        x (np.ndarray): x-axis.
        f (np.ndarray): complex function.
        method (str, optional): Either 'real-imag' or 'norm-arg'. Defaults to 'real-imag'.
        lognorm (bool, optional): Determines if the plots should be log-log. Defaults to False.
    """
    
    if((method == 'real-imag') & (lognorm == False)):
        ax.plot(x, f.real, color = 'blue', label = 'Re')
        ax.plot(x, f.imag, color = 'red', label = 'Im')
        ax.legend()
    
    elif((method == 'real-imag') & (lognorm == True)):
        ax_right = ax.twinx()
        ax.plot(x, f.real, color = 'blue', label = 'Re')
        ax_right.plot(x, f.imag, color = 'red', label = 'Im')
        ax.legend()
        ax_right.legend()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax_right.set_xscale('log')
        ax_right.set_yscale('log')
        
    
    elif(method == 'norm-arg'):
        ax_right = ax.twinx()
        ax.plot(x, np.abs(f), color = 'black', label = '||')
        ax_right.plot(x, np.angle(f), color = 'pink', label = 'angle')
        ax.legend()
        ax_right.legend()
        if(lognorm): 
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax_right.set_xscale('log')
            ax_right.set_yscale('log')






def pannel(results):
    
    #Subpannel functions
    def image_pannel(subfig, sigma, epsp, epsp_scale='linear'):
        
        axes_images = subfig.subplots(1,2)
        
        #sigma(x)
        ax = axes_images[0]
        sigma_image = ax.imshow(sigma[-1], vmin = np.min(sigma), vmax = np.max(sigma))
        to_update.append({'obj':sigma_image, 'data':results.sigma})
        sigma_cbar = subfig.colorbar(sigma_image, aspect=10)
        ax.set_title(r'$\sigma(x)$')
        
        #epsp(x)
        ax = axes_images[1]
        if epsp_scale == 'log':
            epsp_image = ax.imshow(epsp[-1], 
                                norm=LogNorm(vmin = np.min(epsp[-1][epsp[-1]!=0]), 
                                                vmax = np.max(epsp[-1])), 
                                interpolation='none')
        else:
            epsp_image = ax.imshow(epsp[-1], vmin = np.min(epsp[-1]), vmax = np.max(epsp[-1]))    
        
        to_update.append({'obj':epsp_image, 'data':results.epsp})
        
        epsp_cbar = subfig.colorbar(epsp_image, aspect=10)
        ax.set_title(r'$\epsilon_p(x)$')
    
    def parameters_pannel(subfig, results):
        
        axes_parameters = subfig.subplot_mosaic('AC;BC')
        
        #sigmaY(x)
        ax = axes_parameters['A']
        sigmay_mean = results._sigmay_mean
        sigmay_mean[sigmay_mean == float('inf')] = np.nan
        sigmaY_image = ax.imshow(sigmay_mean, interpolation=None)
        sigmaY_cbar = subfig.colorbar(sigmaY_image, aspect=5)
        ax.set_title(r'$<\sigma^Y(x)>$', fontsize=15)
        
        #propagator
        ax = axes_parameters['B']
        propagator_image = ax.imshow(results._propagator, norm = LogNorm())
        ax.set_xticks([])
        ax.set_yticks([])
        propagator_cbar = subfig.colorbar(propagator_image, aspect = 5)
        ax.set_title(r'$G(x)$', fontsize=15)
        
        #Parameters table
        params_dict = {'L':results._L, 
                       '$std(\sigma)$':np.around(results._sigma_std,2), 
                       'seed':results._seed,
                       '':''}
        params_dict.update(results._meta)
        
        table_array = np.hstack([np.array(list(params_dict.keys())).reshape(-1,1),
                                 np.array(list(params_dict.values())).reshape(-1,1)])
        
        ax = axes_parameters['C']
        ax.axis('off')
        table = ax.table(cellText=table_array, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(15)


        
        
    def plots_pannel(subfig, sigmabar, epspbar):
        #TODO:maybe use only results as parameter (or use the one from the "pannel" scope)
        axes_plots = subfig.subplots(1,2)

        #Stress-strain
        ax = axes_plots[0]
        stress_strain = ax.plot(sigmabar + epspbar, sigmabar)[0]
        to_update.append({'obj':(stress_strain,'progressive'), 
                          'data':(results.sigmabar + results.epspbar, results.sigmabar)})
        ax.set_xlabel(r"$\epsilon$")
        ax.set_ylabel(r"$\sigma$")
        
        #Stability distribution
        ax = axes_plots[1]
        
        _, _, stability_bar_containers = ax.hist([0], bins=results.stability_bins_edges,
                                                  ec="black", alpha=0.5, density = True)
        for count, rect in zip(results.stability_hist[-1], stability_bar_containers):
            rect.set_height(count)
        to_update.append({'obj':stability_bar_containers, 'data':results.stability_hist})
            
        stability_kde = ax.plot(*results.stability_kde[-1])[0]
        to_update.append({'obj':(stability_kde, 'full'), 'data': results.stability_kde})
        ax.set_title(r'$P(x)$', fontsize=15)
        ax.set_xlim(results.stability_bins_edges[0], results.stability_bins_edges[-1])
        stability_bins_edges_width = results.stability_bins_edges[1] - results.stability_bins_edges[0]
        ax.set_ylim(0, 0.25 * 1/stability_bins_edges_width) #somewhat arbitrary

        
    def avalanche_pannel(subfig, epsp):
        #TODO: change name, maybe not avalanche
        axes_avalanches = subfig.subplots(1,2)

        #Events
        ax = axes_avalanches[0]
        events = ax.imshow(results.event_maps[-1], vmin=0, vmax=1)
        to_update.append({'obj':events, 'data':results.event_maps})
        ax.set_title('Events')
        
        # #Histogram
        # ax = axes_avalanches[1]
        # _, _, relax_steps_bar_containers = ax.hist(relax_steps[1:last], bins=relax_steps_bins_edges,
        #                                           ec="black", alpha=0.5)
        # ax.set_xscale('log')
        # ax.set_yscale('log')
        # ax.set_ylabel('count', fontsize=12)
        # ax.set_title('Avalanche statistics', fontsize=15)
    
    #Figure
    fig = plt.figure(constrained_layout=True)
    subfigs = fig.subfigures(2,2,wspace=0, hspace=0, width_ratios=[2,1])
    subfigs[0,0].set_facecolor('0.95')
    subfigs[0,1].set_facecolor('0.75')
    subfigs[1,0].set_facecolor('0.75')
    subfigs[1,1].set_facecolor('0.95')
    to_update = []
    
    #Pannels
    #TODO: call with results.sigma[-1] etc.
    image_pannel(subfigs[0,0], results.sigma, results.epsp)
    parameters_pannel(subfigs[0,1], results)
    plots_pannel(subfigs[1,0], results.sigmabar, results.epspbar)
    avalanche_pannel(subfigs[1,1], results.epsp)
    
    #maximize window
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

    #TODO: decide if and how to animate
        # def animate(frame):
        # update_all_axes(index=frame*rate)
    # if(show_animation):
    #     # plt.close('all')
    #     return FuncAnimation(fig, animate, frames=int(np.floor(len(sigma)/rate)) -1 , interval= int(1/fps*1000))
    
    #Interactive
    global tracker #trick: make tracker global so it exists outside "pannel" and the connection remains
    tracker = IndexTracker(fig, to_update, update_function, max_index=2*results._nsteps+1)
    fig.canvas.mpl_connect('key_press_event', tracker.on_press) 
    fig.canvas.mpl_connect('scroll_event', tracker.on_scroll)
    # fig.canvas.mpl_connect('button_press_event', tracker.on_mouse_click)
    
    # #TODO: do the buttons and textbox
    # #add textbox to navigate
    # def submit(index):
    #     try:
    #         index = int(index)
    #         tracker.set_index(index)
    #         update_all_axes(np.clip(int(index), 0, len(sigma)))
    #     except:
    #         pass
    #     text_box.set_val('')
    
    # boxsize = (0.04, 0.06)
    # axbox = subfigs[0,0].add_axes([0, 1-boxsize[1], *boxsize])
    # global text_box
    # text_box = TextBox(axbox, 'step')
    # text_box.on_submit(submit)
    
    # #add button to change scale
    
    # def scale_dynamic(event):
    #     sigma_image.set_clim(vmin=np.min(sigma[tracker.index]), vmax=np.max(sigma[tracker.index]))
    #     epsp_image.set_clim(vmin=np.min(epsp[tracker.index]), vmax=np.max(epsp[tracker.index]))
    #     fig.canvas.draw()
        
    # def scale_last(event):
    #     sigma_image.set_clim(vmin=np.min(sigma[last]), vmax=np.max(sigma[last]))
    #     epsp_image.set_clim(vmin=np.min(epsp[last]), vmax=np.max(epsp[last]))
    
    # buttonsize = (boxsize[0]*2, boxsize[1])
    
    # axbutton_dynamic = subfigs[0,0].add_axes([0, 1-2*buttonsize[1], *buttonsize])
    # global button_dynamic
    # button_dynamic = Button(axbutton_dynamic, 'scale: dynamic')
    # button_dynamic.on_clicked(scale_dynamic)
    
    # axbutton_last = subfigs[0,0].add_axes([0, 1-3*buttonsize[1], *buttonsize])
    # global button_last
    # button_last = Button(axbutton_last, 'scale: last')
    # button_last.on_clicked(scale_last)
    
    

    

#TODO: maybe separate two different things: IndexTracker and Updater (?)
# Also, put IndexTracker outside (have a reusable module)
class IndexTracker:
    def __init__(self, fig, to_update, update_function, max_index = float('inf')):
        self.fig = fig
        self.index = 0 #initialize index
        self.max_index = max_index
        self.to_update = to_update
        self.update_function = update_function
        
    def set_index(self, index):
        self.index = index

    def on_scroll(self, event):        
        #update index
        if event.button == 'up': increment = - int(2**(event.step-1))  
        else: increment = int(2**(-event.step-1))
        self.update_index(increment)
        
        #update figure
        self.update_all(self.index)
    
    def on_press(self, event):
        # print('press', event.key, flush=True)
        
        #update index
        if event.key == 'left': increment = -1
        elif event.key == 'shift+left': increment = -15
        elif event.key == 'right': increment = 1
        elif event.key == 'shift+right': increment = 15
        else: return
        
        self.update_index(increment, clip=False)
        
        #update figure
        self.update_all(self.index)
        
    def on_mouse_click(self, event):
        self.set_index(int(event.xdata))
        self.update_all(self.index)
        
    def update_index(self, increment, clip=True):
        if clip:
            self.index = np.clip(self.index + increment, 0, self.max_index -1) #stop at extreme i values
        else:
            self.index += increment
            self.index = self.index % self.max_index
    
    # @linetimer(unit='s')
    def update_all(self, index):
        for element in self.to_update:
            self.update_function(element['obj'], element['data'], index)
        self.fig.canvas.draw()
        


def update_function(obj, data, index):
    
    #if it is a tuple, it means we have some parameters to extract
    if type(obj) == tuple:
        parameter = obj[1]
        obj = obj[0]
    
    match type(obj):
        
        case mpl.image.AxesImage:
            obj.set_data(data[index])
        
        case mpl.lines.Line2D:
            if parameter=='progressive':
                obj.axes.set_xlim(data[0][0], data[0][index]*1.1) #1.1 to see a bit further
                obj.set_data(data[0][0:index+1], data[1][0:index + 1])
            
            elif parameter=='full':
                obj.set_data(*data[index])
                
            else: warnings.warn("Parameter for Line2D updating must be either 'progressive' or 'full'")
        
        case mpl.container.BarContainer:
            for count, rect in zip(data[index], obj.patches):
                rect.set_height(count)
        
        case _ :
            warnings.warn(f"Don't know how to update {type(obj)}")














def set_alpha(ax, alpha):
    for spine in ax.spines.values():
        spine.set_color((0,0,0,alpha))
    ax.tick_params(axis="x", colors=(0,0,0,alpha))
    ax.tick_params(axis="y", colors=(0,0,0,alpha))
    ax.xaxis.label.set_color((0,0,0,alpha))
    ax.yaxis.label.set_color((0,0,0,alpha))

    for child in ax.get_children():
        try:
            child.set_alpha(alpha)
        except:
            pass
        
        
def focus_on(all_axes, focus_axes, alpha=0.3):
    
    if type(focus_axes) != list:
        focus_axes = [focus_axes]
    
    for ax in all_axes:
        if not(ax in focus_axes):
            set_alpha(ax, alpha)


# #TODO: Make it work using the precomputed statistics
# def show_statistics(epspbar, sigmabar, shift, epsp_map, 
#                                 eps_sample_start=0, n_bins=10, cut_at=1):
    
#     #preparation
#     eps = epspbar+sigmabar #TODO: change with gammabar
#     eps = extend_with_shift(eps,shift)
#     sigmabar = extend_with_shift(sigmabar,shift)
    
    
#     sample_start = np.argwhere(eps>eps_sample_start)[0][0]
    
#     fig, axes = plt.subplots(2,2, figsize=(15,9))
    
#     axes[0,0].plot(eps, sigmabar)
#     axes[0,0].axvline(eps[sample_start], color='red', linestyle='--', 
#                     label=f'# of samples: {len(eps)-sample_start}')
#     axes[0,0].set_xlabel(r'$\epsilon$')
#     axes[0,0].set_ylabel(r'$\sigma$')
#     axes[0,0].legend()
    
    
#     epsp_image = axes[0,1].imshow(epsp_map, vmin = np.min(epsp_map), vmax = np.max(epsp_map))
#     fig.colorbar(epsp_image, aspect=10)
#     axes[0,1].set_title(r'$\epsilon_p(x)$')
        
    
#     axes[1,0].hist(unloadings, bins=n_bins, density=True)
#     axes[1,0].set_xlabel(r'$\Delta \sigma$')
#     axes[1,0].set_ylabel('density')
    
    
#     histogram = axes[1,1].hist(unloadings, bins=bins, density=True, edgecolor='k')
    
#     axes[1,1].set_xscale('log')
#     axes[1,1].set_yscale('log')
#     axes[1,1].set_xlabel(r'$\Delta \sigma$')
#     axes[1,1].set_ylabel('density')
    
#     #Select fitting values and range
#     centers = np.sqrt(bins[0:-1] * bins[1:]) #use geometric means for centers
    
#     if type(cut_at) == list:
#         centers = centers[cut_at[0]:cut_at[1]]
#         values = histogram[0][cut_at[0]:cut_at[1]]
#     else:
#         last_index = int(cut_at*centers.size)
#         centers = centers[0:last_index]
#         values = histogram[0][0:last_index]
    
#     axes[1,1].scatter(centers, values, color='red')
    
#     #Do the power law fit:
#     c, a = power_law_fit(centers, values)
#     x_sample = np.linspace(centers[0], centers[-1], 10)
#     axes[1,1].plot(x_sample, power_law(x_sample, c, a), 
#                  linestyle = '--', color = 'k', label=f'Exponent: {a:.2f}')
#     axes[1,1].legend()