#!

import os
import argparse
import pandas as pd
import numpy as np
import robotexperiments.beauty as beauty
from robotexperiments.formats import EXP_REPO_PATH

# --- Funcs

def get_screened_points(cycle, output_points_ffmt):
    screened_ndx = []
    for c in range(cycle):
        screened_ndx += list(np.loadtxt(output_points_ffmt.format(c,c)))

    return screened_ndx

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
    new_points_ndx_format = '/cycles/cycle_{}/'+experimentID+'_cycle_{}_output_points.ndx'
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

    # sincle cycle
    if isinstance(cycles, int):

        pdf_tmp = np.load(exp_folder+pdf_file_template.format(cycles, cycles))

        screened_points_ndx = get_screened_points(
            cycle=cycles,
            output_points_ffmt=exp_folder + new_points_ndx_format
        )
        new_points_ndx = np.loadtxt(exp_folder + new_points_ndx_format.format(cycles,cycles))

        fig, ax = beauty.get_axes(1,1)
        beauty.plot2D_pdfsurfaceplot(
            df=exp_df,
            pdf=pdf_tmp,
            var1=exp_variables[1],
            var2=exp_variables[0],
            axis=ax,
            screened_points_ndx=list(screened_points_ndx),
            new_points_ndx=list(new_points_ndx),
            show_points=True,
        )
        fig.tight_layout()
        fig.savefig('./generated_plots/'+experimentID+f'_PDF_cycle{cycles}.png')

        fig1, ax1 = beauty.get_axes(1,1)
        beauty.plot2D_entropysurfaceplot(
            df=exp_df,
            pdf=pdf_tmp,
            var1=exp_variables[1],
            var2=exp_variables[0],
            axis=ax1,
            screened_points_ndx=list(screened_points_ndx),
            new_points_ndx=list(new_points_ndx),
            show_points=True,
        )
        fig1.tight_layout()
        fig1.savefig('./generated_plots/'+experimentID+f'_ENTROPY_cycle{cycles}.png')

    elif isinstance(cycles, np.ndarray):

        fig, ax = beauty.get_axes(len(cycles), 3)
        fig1, ax1 = beauty.get_axes(len(cycles), 3)

        for c in cycles:

            c_tmp = int(c+1)

            screened_points_ndx = get_screened_points(
                cycle=c_tmp,
                output_points_ffmt=exp_folder + new_points_ndx_format
            )

            new_points_ndx = np.loadtxt(exp_folder + new_points_ndx_format.format(c_tmp,c_tmp))

            pdf_tmp = np.load(exp_folder + pdf_file_template.format(c_tmp,c_tmp))

            beauty.plot2D_pdfsurfaceplot(
                df=exp_df,
                pdf=pdf_tmp,
                var1=exp_variables[1],
                var2=exp_variables[0],
                axis=ax[c],
                screened_points_ndx=list(screened_points_ndx),
                new_points_ndx=list(new_points_ndx),
                show_points=True,
            )

            beauty.plot2D_entropysurfaceplot(
                df=exp_df,
                pdf=pdf_tmp,
                var1=exp_variables[1],
                var2=exp_variables[0],
                axis=ax1[c],
                screened_points_ndx=list(screened_points_ndx),
                new_points_ndx=list(new_points_ndx),
                show_points=True,
            )

        fig.tight_layout()
        fig.savefig('./generated_plots/'+experimentID+'_PDF.png')
        fig1.tight_layout()
        fig1.savefig('./generated_plots/'+experimentID+'_ENTROPY.png')

