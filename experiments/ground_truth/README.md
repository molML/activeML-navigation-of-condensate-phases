# Computed 'Ground truth'

The folder contains the computed 'ground truth' (GT) extracted from the experiments that were carried out in our work.
The GT was computed collecting all the screened data points for a specific system and used as training set to then predict over the full parameter grid space.

We report the GT results for two systems, the 2D explorations for the Lys-100 Asp-200 system, and its 3D counterpart. The latter GT was built taking into account all the points screened in the former case.

The folders contains the following files:
-   `RoboLab00X_GT.csv` : a dataframe containing the parameter space grid and the computed GT labels, in a `'Phase'` column.
-   `RoboLab00X_GT_labels` : a file containing the list of labels as reported in the `'Phase'` column of the dataframe.
-   `RoboLab008_GT_pdf` : a file containing the array membership probabilities for the two different classes.

In the folder containig the data for the RoboLab007 experiment a Python script is available to plot the results for visual inspection.
```bash
python ./RoboLab007_GT/RoboLab007_plot_GT.py
```