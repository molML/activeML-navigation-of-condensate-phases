# -------------------------------------------------- #
# Script for applying an active learning cycle
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import pprint
from robotexperiments.cycle import active_cycle, append_to_masterfile, extract_validated_points

# --- Variables

experimentID = 'asp250_lys100_NaCl_robotExp0'
cycle_number_tmp = 6
new_points_batch_tmp = 16

classifier_dict_tmp = {
    'kernel': ['*', {'type': 'C', 'constant_value': 1.0}, {'type': 'RBF', 'length_scale': 1.0}],
    'n_restarts_optimizer': 5,
    'max_iter_predict': 200,
    'n_jobs': 3
}

acquisition_mode_tmp = 'exploration'

experiment_cycle_dict_tmp = {
    'experimentID': experimentID,
    'cycle_number' : cycle_number_tmp,
    'search_space_dataset': 'DOE_Asp250_Lys100_manualEpx_3Dim.csv',
    'validated_dataset' : f'{experimentID}_cycle{cycle_number_tmp-1}_validated_points.csv',
    'new_points_batch' : new_points_batch_tmp,
    'classifier_model' : 'GaussianProcessClassifier',
    'classifier_dict': classifier_dict_tmp,
    'acquisition_mode': acquisition_mode_tmp,
    'entropy_accuracy' : 2,
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
    
