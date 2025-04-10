# -------------------------------------------------- #
# Script for running the insilico experiment.
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import pprint
from robotexperiments.formats import GT_FILE_PATH
from robotexperiments.cycle import active_cycle, append_to_masterfile, update_masterfile, insilico_validation

# --- Variables

experimentID = 'RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R2'
validated_datasetID = '{}_cycle_{}_validated_points.csv'
new_points_batch = 32
acquisition_mode = 'exploration'

# - gt
GT_DB = GT_FILE_PATH+'/RoboLab008_GT/RoboLab008_GT.csv'

# - number of total cycles (excluded the zero-th cycle)
N_CYCLES = 21

# --- main

if __name__ == '__main__':

    for cycle in range(N_CYCLES+1):

        classifier_dict = {
            'kernel': ['*', {'type': 'C', 'constant_value': 1.0}, {'type': 'RBF', 'length_scale': 1.0}],
            'n_restarts_optimizer': 5,
            'max_iter_predict': 150,
            'n_jobs': 8
        }

        # - config
        experiment_cycle_dict_tmp = {
            'experimentID': experimentID,
            'cycle_number' : None,
            'search_space_dataset': 'DOE_RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R2_3Dim.csv',
            'search_space_switch_from': None,
            'validated_dataset' : None,
            'new_points_batch' : new_points_batch,
            'classifier_model' : 'GaussianProcessClassifier',
            'classifier_dict': classifier_dict,
            'acquisition_mode': acquisition_mode,
            'entropy_accuracy' : 1,
            'sampling_mode': 'FPS',
        }

        print('# --------------------------------------\n'\
             f'# \tActive Cycle {cycle}     \n'\
              '# --------------------------------------\n'\
             )

        experiment_cycle_dict_tmp['cycle_number'] = cycle

        # locate the validated points
        if cycle > 0:
            experiment_cycle_dict_tmp['validated_dataset'] = validated_datasetID.format(experimentID,
                                                                                        cycle-1)
        print('Config file:')
        pprint.pprint(experiment_cycle_dict_tmp)

        # EXPERIMENTS
        active_cycle(**experiment_cycle_dict_tmp)

        # append to master file
        append_to_masterfile(experimentID=experimentID,
                             cycle_number=cycle,
                             fill_value=0)

        # in-vitro validation from gt dataset for current cycle
        insilico_validation(experimentID=experimentID,
                           cycle_number=cycle,
                           grount_truth_dataset=GT_DB)
        
        # update master file
        update_masterfile(experimentID=experimentID,
                          cycle_number=cycle)
