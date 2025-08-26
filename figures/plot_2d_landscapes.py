#!

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import robotexperiments.beauty as beauty
from robotexperiments.formats import EXP_REPO_PATH

# --- Funcs

def get_screened_points(cycle, output_ponts_ffmt):
    screened_ndx = []
    for c in range(cycle):
        screened_ndx += list(np.loadtxt(output_ponts_ffmt.format(c,c)))

    return screened_ndx


# --- Variables

experimentID = 'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R1'
search_space_dataset = '/dataset/DOE_Asp200_Lys100_150mM_NaCl_matrix_1decimal_R1.csv'

# Target variable
target_variable = 'Phase'

# Standard file names
pdf_file_template = '/cycles/cycle_{}/'+experimentID+'_cycle_{}_output_points_pdf.npy'
new_points_ndx_format = '/cycles/cycle_{}/'+experimentID+'_cycle_{}_output_points.ndx'

# Can be either an int or a np.array of consecutive numbers
# that need to match the numbers of cycles
# cycles = 6
cycles = np.arange(9)

if __name__ == "__main__":

    exp_folder = EXP_REPO_PATH+'/'+experimentID
    exp_df = pd.read_csv(exp_folder+search_space_dataset)
    exp_variables = list(exp_df.drop(columns=[target_variable]).columns)
    assert len(exp_variables) == 2, "Variables found in the search space dataset are more than 2. Check the paths/files."

    # sincle cycle
    if isinstance(cycles, int):

        fig, ax = beauty.get_axes(1,1)

        pdf_tmp = np.load(exp_folder+pdf_file_template.format(cycles, cycles))

        screened_points_ndx = get_screened_points(
            cycle=cycles,
            output_ponts_ffmt=exp_folder+new_points_ndx_format
        )
        new_points_ndx = np.loadtxt(exp_folder+new_points_ndx_format.format(cycles,cycles))

        beauty.plot2D_pdfsurfaceplot(
            df=exp_df,
            pdf=pdf_tmp,
            var1=exp_variables[1],
            var2=exp_variables[0],
            axis=ax,
            constant_var=None,
            screened_points_ndx=list(screened_points_ndx),
            new_points_ndx=list(new_points_ndx),
            show_points=True,
        )
        fig.tight_layout()
        fig.savefig(experimentID+f'_PDF_cycle{cycles}.png')

    elif isinstance(cycles, np.ndarray):

        fig, ax = beauty.get_axes(len(cycles), 3)

        for c in cycles:

            c_tmp = int(c+1)

            screened_points_ndx = get_screened_points(
                cycle=c_tmp,
                output_ponts_ffmt=exp_folder+new_points_ndx_format
            )
            
            new_points_ndx = np.loadtxt(exp_folder+new_points_ndx_format.format(c_tmp,c_tmp))

            pdf_tmp = np.load(exp_folder+pdf_file_template.format(c_tmp,c_tmp))

            beauty.plot2D_pdfsurfaceplot(
                df=exp_df,
                pdf=pdf_tmp,
                var1=exp_variables[1],
                var2=exp_variables[0],
                axis=ax[c],
                constant_var=None,
                screened_points_ndx=list(screened_points_ndx),
                new_points_ndx=list(new_points_ndx),
                show_points=True,
            )
        fig.tight_layout()
        fig.savefig(experimentID+'_PDF.png')