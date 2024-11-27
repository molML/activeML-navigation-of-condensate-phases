# -------------------------------------------------- #
# Script for inferiung convergence of the experiment
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import scipy
import numpy as np
import matplotlib.cm as cm
import robotexperiments.beauty as beauty
from robotexperiments.formats import FOLDERS_TREE

# --- Variables

experimentID = 'RoboLab008_Lys100_Asp200_NaCl_Matrix_R2'

cycle_number_tmp = 3

pdf_file_template = 'cycles\\cycle_{}\\machine_learning\\'+experimentID+'_cycle_{}_output_points_pdf.npy'

# -- dropout parameters
entropy_decimals = 2
x_min, x_max = -0.69, 0.69  # Adjustable range
bin_size = 0.025  # Adjustable bin size
exclude_min, exclude_max = -0.05, 0.05 # Define exclusion range (e.g., from -0.1 to 0.1)
cmap = cm.get_cmap('PiYG')

# --- main

if __name__ == '__main__':

    entropy_dict = {}

    CYCLES_DIR = FOLDERS_TREE['experiments'][experimentID]

    for cycle in range(cycle_number_tmp+1):
        try:
            pdf_tmp = np.load(CYCLES_DIR+pdf_file_template.format(cycle,cycle))

            entropy_tmp = np.around(scipy.stats.entropy(pdf_tmp, axis=1), 
                                    decimals=entropy_decimals)            
            entropy_dict[cycle] = entropy_tmp
        
        except:
            print(f'Cycle {cycle} does not exist.')

    n_total_cycles = len(entropy_dict.keys())
    assert n_total_cycles > 1, f'The computation need at least 2 cycles, but {n_total_cycles} was given ({entropy_dict.keys()})'

    n_samples = len(entropy_tmp)

    delta_entropy_dict = {}

    for i in range(1, n_total_cycles):

        delta_entropy_dict[f'$\Delta H$({i+1}-{i})'] = entropy_dict[i+1] - entropy_dict[i]


    # --- computation of the negative and positive increases
    # Create bins based on the given bin size
    bins = np.arange(x_min, x_max + bin_size, bin_size)

    n_plots = len(delta_entropy_dict.keys())
    fig, ax = beauty.get_axes(n_plots,3)
    fig1, ax1 = beauty.get_axes(1,1, fig_frame=(6.6,3))

    neg_h_list = np.empty(n_plots)
    pos_h_list = np.empty(n_plots)

    y_max = 0
    for i,(k,arg) in enumerate(delta_entropy_dict.items()):

        filtered_d = arg[(arg < exclude_min) | (arg > exclude_max)]
        counts, bin_edges = np.histogram(filtered_d, bins=bins)
        raw_counts, raw_edges = np.histogram(arg, bins=bins)

        neg_h_list[i] = np.sum([counts[c] for c,neg in enumerate(bin_edges[:-1]) if neg < 0]) / np.sum(raw_counts)
        pos_h_list[i] = -np.sum([counts[c] for c,neg in enumerate(bin_edges[:-1]) if neg > 0]) / np.sum(raw_counts)

        # Normalize the bin centers to map to colormap values
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        normed_bin_centers = (bin_centers - bin_centers.min()/2.) / (bin_centers.max()/2. - bin_centers.min()/2.)
        
        # Create colored bars
        bar_colors = cmap(normed_bin_centers)
        ax[i].bar(bin_centers, counts, 
                width=bin_size, color=bar_colors, 
                edgecolor='black', alpha=1.)
        
        ax[i].set_title(k)
        ax[i].set_xlim([x_min, x_max])  # Ensure x-axis limits are consistent
        y_max = max(y_max, max(counts))

    for i in range(n_plots):
        ax[i].set_ylim([0, y_max+(y_max*.1)])
        ax[i].set_ylabel('count')
        ax[i].set_xlabel(r'$\Delta H$')
    fig.tight_layout()
    fig.savefig(CYCLES_DIR+'delta_h_histograms.png')

    ax1.plot(np.arange(n_plots), neg_h_list, ls='-', c=cmap(0.05), label=r'$H(\downarrow)$')
    ax1.plot(np.arange(n_plots), pos_h_list, ls='--', c=cmap(0.85), label=r'$H(\uparrow)$')
    ax1.scatter(np.arange(n_plots), neg_h_list, edgecolors='0.', c=cmap(0.05), zorder=2)
    ax1.scatter(np.arange(n_plots), pos_h_list, edgecolors='0.', c=cmap(0.85), zorder=2)
    ax1.set_xticks(np.arange(n_plots))
    ax1.set_xticklabels(delta_entropy_dict.keys())
    ax1.set_ylabel('fraction of points')
    ax1.grid(ls='--', alpha=.5)
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(CYCLES_DIR+'delta_h_trend.png')
