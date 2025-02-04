# _In-silico_ experiment

In this folder we provide a way of testing the Active Learning Exploration of 3D phase diagrams based on the ground truth that we collected with our experiments.

This folder was set-up to contain a simulation for the 3D phase diagram of p-Lys-100 and p-Asp-200.

## Simulation set-up

The simulation requires a few steps before running it.
All the command were tested with the conda environment created as described in the installation and on a linux machine with Ubuntu 22.04.5 LTS.

-   **Setting up the master file**

```python
python src/script/experiments/init_master_file.py
```
Initialize the master file (more info in the `format.py` module), if not already present.
If already present, it will give a summary of the last available version of it.

-   **Setting up the search space matrix**

```python
python src/script/experiments/experiment_init.py -phasevar config.json
```
Reads the `config.json` file and creates the "naked" (_i.e._, withouth Phase annotaions) search space matrix.