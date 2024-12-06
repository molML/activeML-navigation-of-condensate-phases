# -------------------------------------------------- #
# Script for plotting 2D phase diagram slices
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import robotexperiments.beauty as beauty
from robotexperiments.formats import FOLDERS_TREE

# --- Variables

experimentID = 'asp250_lys100_NaCl_robotExp0'

search_space_dataset = '/dataset/DOE_Asp250_Lys100_manualEpx_3Dim.csv'
var1 = 'Conc_SIGMA_Asp_250_(mM)'
var2 = 'Conc_AP_Lys_100_(mM)'
var3 = 'Conc_NaCl_(mM)'

xyvar = (var1,var2)
zvar = var3

pdf_file_template = '/cycles/cycle_{}/'+experimentID+'_cycle{}_output_points_pdf.npy'

new_points_ndx_format = '/cycles/cycle_{}/'+experimentID+'_cycle{}_output_points.ndx'

cycle_number_tmp = 6

# --- main

if __name__ == '__main__':

    EXPdir = FOLDERS_TREE['experiments'][experimentID]
    df = pd.read_csv(EXPdir+search_space_dataset)

    zvar_value_list = np.unique(df[zvar].values)

    X,Y = xyvar
    Z = zvar

    screened_points_ndx = []
    for i in range(2,cycle_number_tmp+1):

        pdf = np.load(EXPdir+pdf_file_template.format(i,i))

        previous_points_ndx = np.loadtxt(EXPdir+new_points_ndx_format.format(i-1, i-1)).astype(int)
        screened_points_ndx += list(previous_points_ndx)

        new_points_ndx = np.loadtxt(EXPdir+new_points_ndx_format.format(i, i)).astype(int)

        fig, ax = beauty.get_axes(len(zvar_value_list),5)
        fig1, ax1 = beauty.get_axes(len(zvar_value_list),5)

        for j,zv in enumerate(zvar_value_list):
            
            beauty.plot2D_3variable_pdfsurface(df=df, pdf=pdf,
                                               var1=X, var2=Y, constant_var=(zvar,zv),
                                               screened_points_ndx=screened_points_ndx,
                                               new_points_ndx=new_points_ndx,
                                               show_points=True,
                                               axis=ax[j])

            beauty.plot2D_3variable_entropysurface(df=df, pdf=pdf,
                                                   var1=X, var2=Y, constant_var=(zvar,zv),
                                                   screened_points_ndx=screened_points_ndx,
                                                   new_points_ndx=new_points_ndx,
                                                   show_points=True,
                                                   axis=ax1[j])
            
            fig.tight_layout()
            fig.savefig(EXPdir+f'/cycles/figures/{experimentID}_cycle{i}_pdf.png')
            fig1.tight_layout()
            fig1.savefig(EXPdir+f'/cycles/figures/{experimentID}_cycle{i}_entropy.png')