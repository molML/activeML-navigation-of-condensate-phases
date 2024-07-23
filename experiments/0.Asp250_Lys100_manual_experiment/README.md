# Experiment0: Asp250 + Lys100 + salt

This is the first testing experiment, that has been carried out in a hybrid manual/robot mode.
The `README.md` file serves as example for understanding the routine.

Folder organization:
---
0.Asp250_Lys100_manual_experiment/
├── cycles
│   ├── cycle_1
│   │   └── **outputs_1**
│   ├── cycle_2
│   │   └── **outputs_2**
│   ├── cycle_N
│   :   :   :
│      
├── dataset
│   ├── DOE_Asp250_Lys100_manualEpx_3Dim.csv
│   ├── exp_phasevar_config_file.json
│   ├── lys100_asp250_starting_experiments.csv
│   └── phase_diagram_config_asp250_lys100.json
│
└── README.md
---

## Initialization

In the `dataset` folder the starting DOE can be created by running the script

```python
python path/to/exp_scripts/experiment_init.py \
    -phasevar phase_diagram_config_asp250_lys100.json \
    -dfcsv lys100_asp250_starting_experiments.csv
```

Where we also add the existing information of the previously screened points.

## Cycles

The general cycle can be carried out by running the script

```python
python path/to/cycle_scripts/active_learning_cycle.py -c cycle_X_config.yaml
```

Where the file `cycle_X_config.yaml` contains the information about the cycle Xth cycle.

### Cycle_1

From the file `path/cycles/cycle_1/cycle_1_config.yaml`:

```yaml
experimentID: 'asp250_lys100_NaCl_robotExp0'
cycleN: 1
rngSeed: 73

dataset: 'DOE_Asp250_Lys100_manualEpx_3Dim.csv'
targetVariable: 'Phase'

validatedset: #None as we included it in the creation of the DOE

newBatch: 18

clfModel: 'GaussianProcessClassifier'
kParam1: 1.0
kParam2: 1.0
clf_dict: # None for testing

acqMode: 'exploration'
entropyDecimals: 2

screeningSelection: 'FPS'
```

Cycle 1 was run before the setup of the complete pipeline, so there may be incosistencies in the outputs file (some are missing but can be retrieved).


### Cycle_2

From the file `path/cycles/cycle_2/cycle_2_config.yaml`:

```yaml
experimentID: 'asp250_lys100_NaCl_robotExp0'
cycleN: 2
rngSeed: # None for testing

dataset: 'DOE_Asp250_Lys100_manualEpx_3Dim.csv'
targetVariable: 'Phase'

validatedset: '/cycle_1/asp250_lys100_NaCl_robotExp0_cycle1_validated_points.csv'

newBatch: 18

clfModel: 'GaussianProcessClassifier'
kParam1: 1.0
kParam2: 1.0
clf_dict: # testing additional info
  n_restarts_optimizer: 5
  max_iter_predict: 200

acqMode: 'exploration'
entropyDecimals: 2

screeningSelection: 'FPS'
```