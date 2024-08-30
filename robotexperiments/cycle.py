# -------------------------------------------------- #
# Functions for evaluating an active learning cycle
# on a curated dataframe
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import joblib
import numpy as np

from robotexperiments.dataManager import read_validated_df
from robotexperiments.utils import add_keyID_to_dataframe, save_to_jason
from robotexperiments.formats import FOLDERS_TREE, INDICATOR_LABEL, TARGET_LABEL, UNASSIGNED_TARGET_VALUES, OUTPUT_FILE_PATTERN

import activeclf as alclf
from activeclf.learning import active_learning_cycle

from typing import Any

# ------------------------------------------------
# ACTIVE LEARNING
# ------------------------------------------------

# --- main

def active_cycle(
        experimentID: str,
        search_space_dataset: str,
        validated_dataset: str,

        cycle_number: int,
        new_points_batch: int,

        classifier_model: str,
        classifier_dict: dict,
                 
        acquisition_mode: str,
        entropy_accuracy: int=1,
        sampling_mode: str='FPS'
        ) -> None:

    # Init the experiment
    # - set up paths and variables
    # dir with all the experiment files
    experiment_dir_path = FOLDERS_TREE['experiments'][experimentID]
    # dir to save current results
    cycle_output_dir_path = experiment_dir_path + f'/cycles/cycle_{cycle_number}/'
    # TODO: add assert statement and make the dir automatically generated (?)

    # - OUTPUTS
    output_files_name = cycle_output_dir_path+f'{experimentID}_cycle{cycle_number}'

    # local varaibles passed to the function
    save_to_jason(dictonary=locals(),
                  fout_name=output_files_name+f'_config_file')

    # - read the search space dataframe
    data = alclf.DataLoader(
        file_path=experiment_dir_path+'/dataset/'+search_space_dataset,
        target=TARGET_LABEL
    )

    # ----------------------------------------------------------------------------------------------
    # - checks for cycle 0
    if cycle_number == 0:
        print('Cycle 0 assumes no points are known and the search space is completely unexplored.')
        print('The information about the acquisition funciton and the classifier will be skipped.')
        # -- if cycle 0 the new batch of point will be computed accoding to sampling mode
        # assert sampling_mode in SAMPLING_MODE_LIST, f"Error: sampling_mode '{sampling_mode}' is not in the list of modes, {SAMPLING_MODE_LIST}"

        # the new index are the main result of the algorithm as they represent
        # the new points that are going to be screened in the lab

        new_al_indices = alclf.acquisition.pointSampler(mode=sampling_mode).sample(X=data.X,
                                                                                   n=new_points_batch)

    # ----------------------------------------------------------------------------------------------
    # - if cycle number is greater than 0 we assume we can use the clasisfier and the active search
    elif cycle_number > 0:

        # -- checks for validated dataset
        if validated_dataset:
            # read the validated df removing the indicator labels (for merging purpouses)
            validated_df = read_validated_df(df_path=experiment_dir_path + f'/cycles/cycle_{cycle_number-1}/'+validated_dataset,
                                             remove_keys=INDICATOR_LABEL)
            # --- merge (update) the validated points into the search space df and overwrite it
            data.merge_validated_df(
                validated_df=validated_df,
                target=TARGET_LABEL,
                overwrite=True
            )
            print(f'Merging the validated dataframe to main search space dataframe.')
        
        else:
            # the algorithm assumes that cycle 1 can be prepared from previous knowledge
            # already inserted in a dataframe, hence no validation needed from cycle0 as
            # there is no cycle0
            assert cycle_number == 1, 'Validation dataframe not set, and cycle > 1!'

        # - create the feature space
        # - necessary for the active learnig routine (see alclf doc)
        data.feature_space(scaling=True)
    
        print(f'\nCycle n. {cycle_number}\n')
        print('Searching for new points in an active way ...\n')

        # -- set up the classifier function
        # build the kernel object
        kernel_factory = alclf.classification.KernelFactory(kernel_dict=classifier_dict['kernel'])
        # substitue the kernel to dict
        classifier_dict['kernel'] = kernel_factory.get_kernel()

        # the classifier dict must be defined according to the 
        # classifier model chosen
        classifier_func = alclf.ClassifierModel(model=classifier_model, **classifier_dict)

        # -- set up the acquisition function
        acquisition_func = alclf.DecisionFunction(mode=acquisition_mode, 
                                                  decimals=entropy_accuracy)
        # TODO: make the decision accuracy also take a % from the max interval for a smoother the search (?)

        # -- initialize the starting configuration
        # the algo assumes that the un-explored points all have a set target value
        # e.g., -1 (or as defined by the UNASSINED_TARGET_VALUES)
        # TODO: change the referencing in the code using the global variables in the format.py
        known_indices = data.y.index[data.y != UNASSIGNED_TARGET_VALUES].tolist()

        # -- actual cycle

        new_al_indices, new_al_indices_pdf = active_learning_cycle(
            feature_space=(data.X, data.y),
            idxs=known_indices,
            new_batch=new_points_batch,
            clf_func=classifier_func,
            acquisition_func=acquisition_func,
            sampling_mode=sampling_mode
        )

        # -- END of the al cycle
    # ----------------------------------------------------------------------------------------------

    # - generate and add the INDICATOR_LABELS (e.g., Barcodes)
    new_al_points_df, unique_keys = add_keyID_to_dataframe(df=data.df.iloc[new_al_indices],
                                                           col_name=INDICATOR_LABEL,
                                                           generator_mode='custom')

    assert len(unique_keys) == len(set(unique_keys)), f"Error: keys were non uniquely generated!"

    print('\nNew points to validate:')
    print(new_al_points_df)

    # - select only the barcodes for output
    barcode_df = new_al_points_df['Barcode']

    # new al points with barcodes dataframe
    new_al_points_df.to_csv(output_files_name+f'_{OUTPUT_FILE_PATTERN}.csv', index=False)

    # original indicing of new al points (referring to the big dataframe of points)
    np.savetxt(output_files_name+f'_output_points.ndx', new_al_points_df.index.tolist())

    # dataframe containing the barcodes of the new al points
    barcode_df.to_csv(output_files_name+f'_output_barcodes.csv', index=False)

    # classifier and output of the classifier
    if cycle_number > 0:
        np.save(output_files_name+f'_output_points_pdf.npy', new_al_indices_pdf)
        joblib.dump(classifier_func.clf, output_files_name+f'_output_algorithm.pkl')
    
    print(f'\n# END of Cycle {cycle_number}')


# ------------------------------------------------
# APPEND/UPDATE to MASTER
# ------------------------------------------------

import pandas as pd
from robotexperiments.fileManager import MasterFileManager, get_files_from, select_first_item_with_pattern

# --- main append

def append_to_masterfile(experimentID: str,
                         cycle_number: int,
                         fill_value: Any=0) -> None:
    
    # - set the paths
    experiment_dir_path = FOLDERS_TREE['experiments'][experimentID]
    # dir to save current results
    cycle_output_dir_path = experiment_dir_path + f'/cycles/cycle_{cycle_number}/'

    # - init the file manager
    # this will automatically recover the latest version of the 
    # master file (or create it if it's missing)

    manager = MasterFileManager()

    # - read the output files
    # by defaut set to read the .csv files as it expect the output
    # points to be in that form and it search for `format.OUTPUT_FILE_PATTERN`
    # to recognize the points to be added to the master file

    cycle_output_csv_files = get_files_from(folder=cycle_output_dir_path)
    # may be getto
    cycle_output_points_csv = select_first_item_with_pattern(strings=cycle_output_csv_files,
                                                             pattern=OUTPUT_FILE_PATTERN)
    # TODO: improve this (?)

    output_points_df = pd.read_csv(cycle_output_dir_path+cycle_output_points_csv)
    print(f'Output file with not validated points to be appended:\n{cycle_output_points_csv}')

    # - added experiment_ID key for traking AI IDs
    output_points_df['Experiment_ID'] = [experimentID]*len(output_points_df)

    # - merge the data and fill the unknown
    manager.append_data(new_data=output_points_df, 
                        fill_value=fill_value)

    # - saving a new master file version
    manager.save_file(overwrite=False)

    print('# END append to master file')


# --- main update

from robotexperiments.formats import VALIDATED_FILE_PATTERN


def update_masterfile(experimentID: str,
                      cycle_number: int):

    # - set the paths
    experiment_dir_path = FOLDERS_TREE['experiments'][experimentID]
    # dir to save current results
    cycle_output_dir_path = experiment_dir_path + f'/cycles/cycle_{cycle_number}/'

    # - init the file manager
    # this will automatically recover the latest version of the 
    # master file (or create it if it's missing)

    manager = MasterFileManager()

    # - read the output files
    # by defaut set to read the .csv files as it expect the output
    # points to be in that form and it search for `format.VALIDATED_FILE_PATTERN`
    # to recognize the points to be added to the master file.
    # The validated files comes from experimental validation.

    cycle_output_csv_files = get_files_from(folder=cycle_output_dir_path)
    # may be getto
    cycle_validated_points_csv = select_first_item_with_pattern(strings=cycle_output_csv_files,
                                                                pattern=VALIDATED_FILE_PATTERN)
    # TODO: improve this (?)

    validated_points_df = pd.read_csv(cycle_output_dir_path+cycle_validated_points_csv)
    print(f'Output file with validated points:\n{cycle_validated_points_csv}')

    manager.update_data_values(updated_data=validated_points_df,
                               reference_key=INDICATOR_LABEL)
    
    # - save over-write
    manager.save_file(overwrite=True)

    print('# END update the master file')


# ------------------------------------------------
# EXTRACT VALIDATION FROM MASTERFILE
# ------------------------------------------------

from robotexperiments.utils import parse_config
from robotexperiments.formats import VALIDATED_FILE_PATTERN, MAPPING_PHASES


def extract_validated_points(experimentID: str,
                             cycle_number: int) -> None:


    # - set the paths
    experiment_dir_path = FOLDERS_TREE['experiments'][experimentID]
    # dir to save current results
    cycle_output_dir_path = experiment_dir_path + f'/cycles/cycle_{cycle_number}/'
    
    output_file_name = cycle_output_dir_path+f'{experimentID}_cycle{cycle_number}'+f'_{VALIDATED_FILE_PATTERN}.csv'

    dataset_dir_path = experiment_dir_path + '/dataset/'
    dataset_init_file = get_files_from(folder=dataset_dir_path,
                                       ew='.json',
                                       verbose=False)[0]
    # get the experimental columns
    dataset_init_dict = parse_config(filename=dataset_dir_path+dataset_init_file)
    dataset_columns = list(dataset_init_dict['phase_diagram_variables'].keys())

    manager = MasterFileManager(verbose=False)

    # assumes the master file has been updated
    master_df = manager.master_df

    # load barcodes
    barcodes_file = get_files_from(folder=cycle_output_dir_path,
                                   ew='barcodes.csv', 
                                   verbose=False)[0]
    
    barcodes = pd.read_csv(cycle_output_dir_path+barcodes_file)[INDICATOR_LABEL].to_numpy()

    validated_points_df = master_df[master_df[INDICATOR_LABEL].isin(barcodes)][dataset_columns]
    validated_points_df[TARGET_LABEL] = validated_points_df[TARGET_LABEL].map(MAPPING_PHASES)

    print(f'Validated points dataframe:\n{validated_points_df}')

    validated_points_df.to_csv(output_file_name, index=False)

    print(f'Saved to: {output_file_name}')
