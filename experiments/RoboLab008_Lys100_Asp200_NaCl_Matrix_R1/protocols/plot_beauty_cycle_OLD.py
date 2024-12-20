# -------------------------------------------------- #
# Script for applying an active learning cycle
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import robotexperiments.beauty as beauty
from robotexperiments.formats import FOLDERS_TREE
import os

# --- Variables
experimentID = 'RoboLab008_Lys100_Asp200_NaCl_Matrix_R1'
cycle_number_tmp = 0


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

    pdf = np.load(EXPdir+pdf_file_template.format(cycle_number_tmp,cycle_number_tmp))

    X,Y = xyvar
    Z = zvar

    screened_points_ndx = []
    for i in range(cycle_number_tmp):
        try:
            previous_points_ndx = np.loadtxt(EXPdir+new_points_ndx_format.format(i, i)).astype(int)
            screened_points_ndx += list(previous_points_ndx)
        except:
            pass

    new_points_ndx = np.loadtxt(EXPdir+new_points_ndx_format.format(cycle_number_tmp, cycle_number_tmp)).astype(int)

    beauty_folder = EXPdir+f'cycles\\cycle_{cycle_number_tmp}\\machine_learning\\figures\\'
    try:
        os.mkdir(beauty_folder)
    except:
        print(f'folder alredy exists: {beauty_folder}')
    for zv in zvar_value_list[:]:
        fig, ax = beauty.get_axes(1,1)
        # beauty.plot2D_3variable_points(df=df,
        #                                var1=X,
        #                                var2=Y,
        #                                constant_var=(zvar,zv),
        #                                screened_points_ndx=screened_points_ndx,
        #                                new_points_ndx=new_points_ndx,
        #                                axis=ax[0])
        
        beauty.plot2D_3variable_pdfsurface(df=df,
                                           pdf=pdf,
                                           var1=X,
                                           var2=Y,
                                           constant_var=(zvar,zv),
                                           screened_points_ndx=screened_points_ndx,
                                           new_points_ndx=new_points_ndx,
                                           show_points=True,
                                           axis=ax)

        # beauty.plot2D_3variable_entropysurface(df=df,
        #                                        pdf=pdf,
        #                                        var1=X,
        #                                        var2=Y,
        #                                        constant_var=(zvar,zv),
        #                                        screened_points_ndx=screened_points_ndx,
        #                                        new_points_ndx=new_points_ndx,
        #                                        show_points=True,
        #                                        axis=ax[2])
        fig.tight_layout()
        
        fig.savefig(beauty_folder+f'{experimentID}_cycle_{cycle_number_tmp}_{var3}-{zv}.png')