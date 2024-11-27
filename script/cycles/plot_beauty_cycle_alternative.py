# -------------------------------------------------- #
# Script for plotting 2D phase diagram slices
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
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

algorithm_file_format = '/cycles/cycle_{}/'+experimentID+'_cycle{}_output_algorithm.pkl'

output_points_format = '/cycles/cycle_{}/'+experimentID+'_cycle{}_output_points.csv'

cycle_number_tmp = 3

# --- main

if __name__ == '__main__':

    EXPdir = FOLDERS_TREE['experiments'][experimentID]
    df = pd.read_csv(EXPdir+search_space_dataset)
    
    matrix = df.drop(columns='Phase')
    matrix = StandardScaler().fit_transform(matrix)

    zvar_value_list = np.unique(df[zvar].values)
    print(zvar_value_list)

    X,Y = xyvar
    Z = zvar

    screened_points_ndx = []

    for i in range(3,cycle_number_tmp+1):

        if i == 0:
            # screened_points = pd.read_csv(EXPdir+output_points_format.format(i,i))
            pass

        elif i > 0:
            
            model = joblib.load(EXPdir+algorithm_file_format.format(i,i))
            pdf = model.predict_proba(matrix)

            fig, ax = beauty.get_axes(len(zvar_value_list),6)
            fig1, ax1 = beauty.get_axes(len(zvar_value_list),6)

            for j,zv in enumerate(zvar_value_list[:]):

                beauty.plot2D_3variable_pdfsurface(df=df,
                                                pdf=pdf,
                                                var1=X,
                                                var2=Y,
                                                constant_var=(zvar,zv),
                                                screened_points_ndx=None,
                                                new_points_ndx=None,
                                                show_points=False,
                                                axis=ax[j])

                beauty.plot2D_3variable_entropysurface(df=df,
                                                pdf=pdf,
                                                var1=X,
                                                var2=Y,
                                                constant_var=(zvar,zv),
                                                screened_points_ndx=None,
                                                new_points_ndx=None,
                                                show_points=False,
                                                axis=ax1[j])

    fig.tight_layout()
    fig.savefig('test.png')
    fig1.tight_layout()
    fig1.savefig('test1.png')