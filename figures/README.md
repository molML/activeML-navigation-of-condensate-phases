# Raw data and figures generation

In this folder are contained the original and the respective raw-data for the figures presented in the _main_ manuscript.

Additionally two scripts (`plot_2d_landscapes.py`, `plot_3d_landscapes.py`) are provided to replicate the plots of the phase diagrams and the entropy landscapes that are reported in both the main manuscript and the supporting information.

To used the script is it is necessary to change the following fields:
-   `experimentID`, needs to match the specific folder of the experiments in the experiments folder.
-   `search_space_dataset`, needs to match the `DOE_*` file that is present in the `/experimentID/dataset` folder.
-   `cycles`, which can be a `int` or a `np.array` of ints with the corresponding number/s of cycle/s that are going to be drawn.

Once the parameters are set one can simply run the command:

```python
python plot_2d_landscapes.py -expid EXP_ID -tcycles 9
```

for a 2D series of plots, or

```python
python plot_3d_landscapes.py -expid EXP_ID -tcycles 21
```

for a 3D series of plots.

In case of 3D the plots are always individually saves as `.pdf` and they do not occupy a single figure object.
The figure are stored by default in the folder `generated_plots`, where currently there are some examples.

A list of all the 2D experiments `expID` conducted in the lab:
```
RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R1/
RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R2/
RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R3/
RoboLab009_Lys100_Asp100_150mM_NaCl_2Dmatrix_R1/
RoboLab010_Lys100_Asp30_150mM_NaCl_2Dmatrix_R1/
RoboLab011_Lys250_Asp30_150mM_NaCl_2Dmatrix_R2/
RoboLab012_Lys250_Asp100_150mM_NaCl_2Dmatrix_R2/
RoboLab013_Lys250_Asp200_150mM_NaCl_2Dmatrix_R2/
RoboLab014_Lys20_Asp30_150mM_NaCl_2Dmatrix_R2/
RoboLab015_Lys20_Asp100_150mM_NaCl_2Dmatrix_R2/
RoboLab016_Lys20_Asp200_150mM_NaCl_2Dmatrix_R2/
```

**Disclaimer**: regardless all data used in the paper is stored in the `root_dir/experiments/` folder, under each single experiment.