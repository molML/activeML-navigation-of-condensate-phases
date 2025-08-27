#!

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import robotexperiments.beauty as beauty
from robotexperiments.formats import EXP_REPO_PATH

# --- Variables

experimentID = 'RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R1'
search_space_dataset = '/dataset/DOE_RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R1_3Dim.csv'

# Target variable
target_variable = 'Phase'

# Standard file names
pdf_file_template = '/cycles/cycle_{}/'+experimentID+'_cycle_{}_output_points_pdf.npy'

# Can be either an int or a np.array of consecutive numbers
# that need to match the numbers of cycles
cycles = 21
# cycles = np.arange(2)

if __name__ == "__main__":

    exp_folder = EXP_REPO_PATH+'/'+experimentID
    exp_df = pd.read_csv(exp_folder+search_space_dataset)

    # sincle cycle
    if isinstance(cycles, int):

        if cycles == 0:
            raise ValueError('Cycle must be >0.')

        pdf_tmp = np.load(exp_folder+pdf_file_template.format(cycles, cycles))

        fig = beauty.plot3D_surface_volume_landscape(
            df=exp_df,
            pdf=pdf_tmp,
            show_surfaces=True
        )

        fig.write_image('./generated_plots/'+experimentID+f'_PDF_cycle{cycles}.pdf', scale=2)

    elif isinstance(cycles, np.ndarray):

        for c in cycles:

            c_tmp = int(c+1)

            pdf_tmp = np.load(exp_folder+pdf_file_template.format(c_tmp,c_tmp))

            fig = beauty.plot3D_surface_volume_landscape(
                df=exp_df,
                pdf=pdf_tmp
            )

            fig.write_image('./generated_plots/'+experimentID+f'_PDF_cycle{c_tmp}.pdf', scale=2)