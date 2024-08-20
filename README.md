# RobotLabExperiments

Repository intended for storing and managing the files generated during the Robotlab experiments.

Folder organization:
------------
    master_file/
    ├── master_file_version_0.csv
    ├── master_file_version_1.csv
    └── master_file_version_N.csv

    experiments/
    └── 1.experimentID
        ├── cycles
        │   ├── cycle_0
        │   │   ├── experimentID_cycle0_ouput_points.csv
        │   │   ├── experimentID_cycle0_ouput_points.ndx
        │   │   ├── experimentID_cycle0_ouput_points_pdf.npy
        │   │   ├── experimentID_cycle0_ouput_barcodes.csv 
        │   │   ├── experimentID_cycle0_ouput_algorithm.pkl 
        │   │   ├── experimentID_cycle0_validated_points.csv
        │   │   └── experimentID_cycle0_config_file.json
        │   ├── cycle_1
        │   │   ├── experimentID_cycle1_ouput_points.csv
        │   │   ├── experimentID_cycle1_ouput_points.ndx
        │   │   ├── ...
        │   │   └── ...
        │   └── cycle_N
        │
        └── dataset
            ├── DOE_experimentID.csv
            └── phase_diagram_config_experimentXXX.json
------------

## Setting up the experiment

The setup for the experiments requires a few steps:
-   setting up the directory tree,
-   creating the experimental points that will be screened and evaluated during the cycles.

The `robotexperiments/format.py` file contains core information about the experiments, the master-file, and other essential global variables to run the experiments.

### Master-file

The master-file is the main storing file for all the screened points in all the experiments and it will also guide the robot in the preparation of samples.

The _master-file_ can be initialized (according to the format defined) by running
```python
from robotexperiments.fileManager import fileManager
manager = fileManager()
```
this will create the empty columns for the file and allow other type of actions, like appending, updating and saving different versions of the master file.

### Experiment search-space dataframe

To create the dataframe containing the points to be screened by the algorithm we can run the script from the `script_experiments` folder:
```bash
python src/script_experiments/experiment_init.py -phasevar phasevar_config.json
```
The script needs an input file containing instructions on the ranges of the experimental values of the variables to screen during the experiments.
This is a sample of input config file, used to create the experimental dataset:

```json
{
    "Experiment_ID" : "ExpID_XXX",
    "phase_diagram_variables" : {
        "X" : {"start":0.1, "end":8.0, "ev":0.1},
        "Y" : {"start":0.1, "end":8.0, "ev":0.1},
        "Z" : {"start":100, "end":2000, "ev":100},
        "Phase" : -1
    }
}
```
where a 3D space of variables is assembled with the target property being the `Phase`.  

## Running the cycles

To run the experiments the [ActiveLearningCLassiFier](https://github.com/AGardinon/ActiveLearningCLassiFier) package is required.
The package allow to apply the point selection and classification strategies to an input dataset for each cycle.

The general cycle is evaluated by running the `active_learning_cycle.py` from the `script_cycle` folder:
```bash
python src/script_cycles/active_learning_cycle.py
```
The script input dictionary needs to be adjusted depending on the needs and it contains all the information about the experiment cycle.

### Input dictionary

The input dictionary is defined inside the script (for now) but it can be leverage for automatic experiments.

```python
# --- Variables

experimentID = 'robot001'
cycle_number_tmp = 1
new_points_batch_tmp = 18

classifier_dict_tmp = {
    'kernel': ['*', {'type': 'C', 'constant_value': 1.0}, {'type': 'RBF', 'length_scale': 1.0}],
    'n_restarts_optimizer': 5,
    'max_iter_predict': 150,
    'n_jobs': 3
}

acquisition_mode_tmp = 'exploration'

experiment_cycle_dict_tmp = {
    'experimentID': experimentID,
    'cycle_number' : cycle_number_tmp,
    'search_space_dataset': 'DOE_robot001_3Dim.csv',
    'validated_dataset' : f'/{experimentID}_validated_points.csv', # or None
    'new_points_batch' : new_points_batch_tmp,
    'classifier_model' : 'GaussianProcessClassifier',
    'classifier_dict': classifier_dict_tmp,
    'acquisition_mode': acquisition_mode_tmp,
    'entropy_accuracy' : 1,
    'sampling_mode': 'FPS',
}
```

The code is easily extendable to a loop over multiple cycles, batch of points, acquisition functions or other variables.

Once the cycle is over a bunch of outputs will be generated:
-   csv containig the new batch of points to screen
-   barcode identifiers of the new batch of points
-   original indeces of the points
-   classifier model pkl
-   probability distribution function evaluated over the entire search space
-   json file containing the input configuration

Additionally, at the end of each cycle a few actions are run:
1.  the new points (not validated) are appended to the master file
2.  the points are validated (robot experiment)
3.  the master file is updated with the validated points

Point 1. is taken care automatically from the `active_learning_cycle.py` script
```python
from robotexperiments.cycle import append_to_masterfile

append_to_masterfile(experimentID=experimentID,
                     cycle_number=cycle_number_tmp,
                     fill_value=0)
```

Point 2. is carried out with the robot.

Point 3. assumes that a file `experimentID_validated_points.csv` is created in the cycle folder containig all the information that the `experimentID_output_points.csv` contains but with the validated value of the target variable.
The master file can be upgraded in a similar way:
```python
from robotexperiments.cycle import update_masterfile

update_masterfile(experimentID=experimentID,
                  cycle_number=cycle_number_tmp,
                  fill_value=0)
```
