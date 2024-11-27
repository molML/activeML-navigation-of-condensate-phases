# -------------------------------------------------- #
# Script for applying an active learning cycle
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import pprint
from robotexperiments.cycle import active_cycle, append_to_masterfile, extract_validated_points
import sys
import os

# --- Variables

experimentID = 'RoboLab008_Lys100_Asp200_NaCl_Matrix_R2'
cycle_number_tmp = 'automatic'  # Default "automatic". Picks the latest cycle automatically. Alternatively, use "0" for the first cycle, etc..
new_points_batch_tmp = 32  # 2Dmatrix


# --- AUTOMATIC CYCLE FINDER

cycles_folder = f"E:\\RoboLabExperiments\\experiments\\{experimentID}\\cycles"

if cycle_number_tmp == "automatic":
    # Get a list of all subfolders in the cycles folder
    cycles_subfolders = [f for f in os.listdir(cycles_folder) if os.path.isdir(os.path.join(cycles_folder, f)) and f.startswith('cycle_')]
    
    # Extract the cycle number from each folder and sort them
    cycle_numbers = sorted([int(f.split('_')[1]) for f in cycles_subfolders])
  
    for i in range(len(cycle_numbers)):
        current_cycle_num = cycle_numbers[i]
        next_cycle_num = current_cycle_num + 1
        
        # Check if the notebook protocol exists for the current cycle
        barcode_path = os.path.join(cycles_folder, f"cycle_{current_cycle_num}", "machine_learning", f"{experimentID}_cycle_{current_cycle_num}_output_barcodes.csv")
        validated_path = os.path.join(cycles_folder, f"cycle_{current_cycle_num}", "machine_learning", f"{experimentID}_cycle_{current_cycle_num}_validated_points.csv")

        # Check if the next cycle exists
        next_cycle_folder = os.path.join(cycles_folder, f"cycle_{next_cycle_num}")
        next_cycle_exists = os.path.exists(next_cycle_folder)
          
        if not os.path.exists(barcode_path):
            # If the file does not exist, check if there are higher-numbered cycles and raise a warning
            latest_cycle_number = max(cycle_numbers)
            if current_cycle_num < latest_cycle_number:
                print(f"Warning: cycle_{current_cycle_num} is incomplete while later cycles exist.")
                print(f"Warning: Verify that (future) empty cycle folder are removed.")
                print(f"Consider using the argument cycle_name='cycle_{current_cycle_num}' instead of automatic to complete cycle_{current_cycle_num}.")
                print("Stopping script now...")
                sys.exit()
            else:
                print(f"Warning: The folder for cycle_{current_cycle_num} already exists but has no barcodes.")
                print(f"The folder for cycle_{current_cycle_num} might be empty.")
                print(f"Warning: To run this script, you should remove the folder cycle_{latest_cycle_number}. First verify that this folder is empty.")
                sys.exit()
            # Set the cycle_name to the current incomplete cycle and break the loop
            cycle_number_tmp = f"cycle_{current_cycle_num}"
            
    else:
        if len(cycle_numbers) == 0:
            cycle_number_tmp = 0
        else:
            # If all cycles have the classification file, select the latest one
            latest_cycle_number = max(cycle_numbers)+1
            cycle_number_tmp = latest_cycle_number

print("Starting machine_learning script for cycle: ", cycle_number_tmp)


# --- DO NOT CHANGE THIS PART

classifier_dict_tmp = {
    'kernel': ['*', {'type': 'C', 'constant_value': 1.0}, {'type': 'RBF', 'length_scale': 1.0}],
    'n_restarts_optimizer': 5,
    'max_iter_predict': 150,
    'n_jobs': 16
}

acquisition_mode_tmp = 'exploration'

experiment_cycle_dict_tmp = {
    'experimentID': experimentID,
    'cycle_number' : cycle_number_tmp,
    'search_space_dataset': 'DOE_Asp200_Lys100_NaCl_Matrix_R2.csv',
    'search_space_switch_from': None, # only useful for dataset switches, do not change otherwise
    'validated_dataset' : f'{experimentID}_cycle_{cycle_number_tmp - 1}_validated_points.csv',
    'new_points_batch' : new_points_batch_tmp,
    'classifier_model' : 'GaussianProcessClassifier',
    'classifier_dict': classifier_dict_tmp,
    'acquisition_mode': acquisition_mode_tmp,
    'entropy_accuracy' : 1,  # DO NOT CHANGE, DEFAULT IS 2
    'sampling_mode': 'FPS',
}

# --- main

if __name__ == '__main__':

    print('# --------------------------------------\n'\
         f'# \tActive Cycle {cycle_number_tmp}     \n'\
          '# --------------------------------------\n'\
          )

    print('Evaluation Config:')
    pprint.pprint(experiment_cycle_dict_tmp)

    # if cycle is 0, the validate points are None
    if cycle_number_tmp == 0:
        experiment_cycle_dict_tmp['validated_dataset'] = None

    # if the cycle is > 0 it will extract the validated points from the cycle-1
    elif experiment_cycle_dict_tmp['cycle_number'] > 0:
        extract_validated_points(experimentID=experimentID, cycle_number=cycle_number_tmp-1)

    # - do the cycle
    active_cycle(**experiment_cycle_dict_tmp)

    print('Appending new points to master file for validation.\n')

    # - append to master
    append_to_masterfile(experimentID=experimentID,
                         cycle_number=cycle_number_tmp,
                         fill_value=0)
    
