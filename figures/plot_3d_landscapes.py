#!

import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import robotexperiments.beauty as beauty
from robotexperiments.formats import EXP_REPO_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment runner")
    parser.add_argument("-expid", "--experimentID", required=True, type=str, help="Experiment ID (folder name)")
    parser.add_argument("-tcycles", "--total_cycles", required=False, default=None, type=int, help="Number of total cycles to plot")
    parser.add_argument("-scycle", "--single_cycle", required=False, default=None, type=str, help="Single cycle to plot")
    args = parser.parse_args()
    experimentID = args.experimentID
    tot_cycles = args.total_cycles
    single_cycle = args.single_cycle

    if tot_cycles is None:
        assert single_cycle is not None, "One option must be selected between total_cycles and single_cycle"
        cycles = int(single_cycle)
    elif tot_cycles is not None:
        cycles = np.arange(tot_cycles)

    # Standard file names
    pdf_file_template = '/cycles/cycle_{}/'+experimentID+'_cycle_{}_output_points_pdf.npy'
    target_variable = 'Phase'

    exp_folder = os.path.join(EXP_REPO_PATH, experimentID)
    dataset_folder = exp_folder + '/dataset/'
    print(f"Experiment folder: {exp_folder}")
    print(f"Dataset folder: {dataset_folder}")

    # Find first file starting with DOE_
    files = sorted(f for f in os.listdir(dataset_folder) if f.startswith("DOE_"))
    if not files:
        raise FileNotFoundError(f"No file starting with DOE_ found in {dataset_folder}")
    search_space_dataset = files[0]  # take first occurrence

    # Load dataset
    exp_df = pd.read_csv(os.path.join(dataset_folder, search_space_dataset))
    exp_variables = list(exp_df.drop(columns=[target_variable]).columns)
    assert len(exp_variables) == 2, (
        "Variables found in the search space dataset are more than 2. "
        "Check the paths/files."
    )

    # single cycle
    if isinstance(cycles, int):

        if cycles == 0:
            raise ValueError('Cycle must be >0.')

        pdf_tmp = np.load(exp_folder + pdf_file_template.format(cycles, cycles))

        fig = beauty.plot3D_surface_volume_landscape(
            df=exp_df,
            pdf=pdf_tmp,
            show_surfaces=True
        )

        fig.write_image('./generated_plots/'+experimentID+f'_PDF_cycle{cycles}.pdf', scale=2)

    elif isinstance(cycles, np.ndarray):

        for c in cycles:

            c_tmp = int(c+1)

            pdf_tmp = np.load(exp_folder + pdf_file_template.format(c_tmp,c_tmp))

            fig = beauty.plot3D_surface_volume_landscape(
                df=exp_df,
                pdf=pdf_tmp
            )

            fig.write_image('./generated_plots/'+experimentID+f'_PDF_cycle{c_tmp}.pdf', scale=2)