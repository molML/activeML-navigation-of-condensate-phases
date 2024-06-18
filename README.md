# RobotLabExperiments

Repository intended for storing and managing the files generated during the Robotlab experiments.

Folder organization:
------------
    master_file/
    ├── master_file_version_0.csv
    ├── master_file_version_1.csv
    └── master_file_version_N.csv

    experiments/
    └── 1.experimentXXX
        ├── cycles
        │   ├── cycle_0
        │   │   ├── experimentXXX_ouput_points.csv
        │   │   ├── experimentXXX_ouput_points.ndx
        │   │   └── cycle_0_config.yaml
        │   ├── cycle_1
        │   │   ├── experimentXXX_ouput_points.csv
        │   │   ├── experimentXXX_ouput_points.ndx
        │   │   └── cycle_1_config.yaml
        │   └── cycle_N
        │
        └── dataset
            ├── DOE_experimentXXX.csv
            └── phase_diagram_config_experimentXXX.json
------------

## Runnig the experiments

To run the experiments the [ActiveLearningCLassiFier](https://github.com/AGardinon/ActiveLearningCLassiFier) package is required.
The package allow to apply the point selection and classification strategies to an input dataset for each cycle.

The general cycle is evaluated by running the `script.py` provided in the repository:
```bash
python src/script/activeCLFexperiment.py -c experiment_config.yaml
```
The `experiment_config.yaml` needs to be adjusted depending on the needs of the cycle.
In the following I will provide a couple of practical examples.

### Running $Cycle0$

$Cycle0$  