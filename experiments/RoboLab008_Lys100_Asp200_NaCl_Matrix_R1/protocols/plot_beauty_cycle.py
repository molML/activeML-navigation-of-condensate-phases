# -------------------------------------------------- #
# Script for plotting 2D phase diagram slices
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import robotexperiments.beauty as beauty
from robotexperiments.formats import FOLDERS_TREE

# --- Variables

# --- Variables
experimentID = 'RoboLab008_Lys100_Asp200_NaCl_Matrix_R1'
cycle_number_tmp = 4


search_space_dataset = '\\dataset\\DOE_Asp200_Lys100_NaCl_Matrix_R1.csv'
var1 = 'Conc_AP_Asp_200_(mM)'
var2 = 'Conc_AP_Lys_100_(mM)'
var3 = 'Conc_NaCl_(mM)'

xyvar = (var1,var2)
zvar = var3

pdf_file_template = 'cycles\\cycle_{}\\machine_learning\\'+experimentID+'_cycle_{}_output_points_pdf.npy'
new_points_ndx_format = 'cycles\\cycle_{}\\machine_learning\\'+experimentID+'_cycle_{}_output_points.ndx'

# --- main

if __name__ == '__main__':

    EXPdir = FOLDERS_TREE['experiments'][experimentID]
    df = pd.read_csv(EXPdir+search_space_dataset)

    zvar_value_list = np.unique(df[zvar].values)

    X,Y = xyvar
    Z = zvar

    beauty_folder = EXPdir+f'cycles\\cycle_{cycle_number_tmp}\\machine_learning\\figures\\'
    try:
        os.mkdir(beauty_folder)
    except:
        print(f'folder alredy exists: {beauty_folder}')

    screened_points_ndx = []
    for i in range(1,cycle_number_tmp+1):

        pdf = np.load(EXPdir+pdf_file_template.format(i,i))

        previous_points_ndx = np.loadtxt(EXPdir+new_points_ndx_format.format(i-1, i-1)).astype(int)
        screened_points_ndx += list(previous_points_ndx)

        new_points_ndx = np.loadtxt(EXPdir+new_points_ndx_format.format(i, i)).astype(int)

        # CHANGE HERE FOR THE NUMBER OF PLOTS TO BE DISPLAYED IN
        # A ROW, NOW ITS 8
        fig, ax = beauty.get_axes(len(zvar_value_list),8)
        fig1, ax1 = beauty.get_axes(len(zvar_value_list),8)

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
            fig.savefig(beauty_folder+f'{experimentID}_cycle_{i}_pdf.png')
            fig1.tight_layout()
            fig1.savefig(beauty_folder+f'{experimentID}_cycle_{i}_entropy.png')
