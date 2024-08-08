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
from robotexperiments.formats import FOLDERS_TREE, INDICATOR_LABEL, TARGET_LABEL, UNASSINED_TARGET_VALUES

import activeclf as alclf
from activeclf.learning import active_learning_cycle

# --- variables

SAMPLING_MODE_LIST = ['FPS', 'random']

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
    cycle_output_dir_path = experiment_dir_path + f'/cycles/cycle_{cycle_number}'
    # TODO: add assert statement and make the dir automatically generated (?)

    # - read the search space dataframe
    data = alclf.DataLoader(
        file_path=experiment_dir_path+'/dataset/'+search_space_dataset,
        target=TARGET_LABEL
    )

    # - create the feature space
    # - necessary for the active learnig routine (see alclf doc)
    data.feature_space(scaling=True)

    # ----------------------------------------------------------------------------------------------
    # - checks for cycle 0
    if cycle_number == 0:
        print('Cycle 0 assumes no points are known and the search space is completely unexplored.')
        print('The information about the acquisition funciton and the classifier will be skipped.')
        # -- if cycle 0 the new batch of point will be computed accoding to sampling mode
        assert sampling_mode in SAMPLING_MODE_LIST, f"Error: sampling_mode '{sampling_mode}' is not in the list of modes, {SAMPLING_MODE_LIST}"

        # the new index are the main result of the algorithm as they represent
        # the new points that are going to be screened in the lab

        if sampling_mode == 'FPS':
            new_al_indices = alclf.acquisition.sampling_fps(X=data.X, 
                                                            n=new_points_batch)
        elif sampling_mode == 'random':
            new_al_indices = alclf.acquisition.sampling_rand(X=data.X,
                                                             n=new_points_batch)

    # ----------------------------------------------------------------------------------------------
    # - if cycle number is greater than 0 we assume we can use the clasisfier and the active search
    elif cycle_number > 0:

        # -- checks for validated dataset
        if validated_dataset:
            # read the validated df removing the indicator labels (for merging purpouses)
            validated_df = read_validated_df(df_path=experiment_dir_path + f'/cycles/cycle_{cycle_number-1}',
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
    
        print(f'\nCycle n. {cycle_number}\n')
        print('Searching for new points in an active way ...\n')

        # -- set up the classifier function
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
        known_indices = data.y.index[data.y != UNASSINED_TARGET_VALUES].tolist()

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

    # - OUTPUTS
    output_files_name = cycle_output_dir_path+f'{experimentID}_cycle{cycle_number}'

    # new al points with barcodes dataframe
    new_al_points_df.to_csv(output_files_name+f'_output_points.csv', index=False)

    # original indicing of new al points (referring to the big dataframe of points)
    np.savetxt(output_files_name+f'_ouput_points.ndx', new_al_points_df.index.tolist())

    # dataframe containing the barcodes of the new al points
    barcode_df.to_csv(output_files_name+f'_ouput_barcodes.csv', index=False)

    # classifier and output of the classifier
    if cycle_number > 0:
        np.save(output_files_name+f'_ouput_points_pdf.npy', new_al_indices_pdf)
        joblib.dump(classifier_func.clf, output_files_name+f'_ouput_algorithm.pkl')

    # local varaibles passed to the function
    save_to_jason(dictonary=locals(),
                  fout_name=output_files_name+f'_config_file')
    
    print(f'\n# End of Cycle {cycle_number}')