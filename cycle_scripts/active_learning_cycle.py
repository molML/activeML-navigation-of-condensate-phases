# -------------------------------------------------- #
# Script for applying an active learning cycle
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import argparse
import yaml
import joblib
import numpy as np
import pandas as pd
from typing import Union, List

from coacervateOpti.dataManager import remove_columns
from coacervateOpti.utils import add_keyID_to_dataframe

import activeclf as alclf
from activeclf.learning import active_learning_cycle

# --- func

def read_validated_df(df_path: str, remove_keys: Union[List[str], str]=None) -> pd.DataFrame:
    validated_df = pd.read_csv(df_path)
    if remove_keys:
        validated_df = remove_columns(df=validated_df, key=remove_keys)
    return validated_df

# --- main

def main(argument):
    # -
    # read the file and store it as a dict
    cycle_config = yaml.load(open(argument.config, 'r'), Loader=yaml.FullLoader)
    
    # -
    # read the experiment information
    data = alclf.DataLoader(file_path=cycle_config['dataset'], 
                            target=cycle_config['targetVariable'])
    
    if cycle_config['validatedset'] is not None:
        print(f'Merging {cycle_config['validatedset']}')
        validated_df = read_validated_df(df_path=cycle_config['validatedset'],
                                         remove_keys='Barcode')
        data.merge_validated_df(
            validated_df=validated_df,
            target=cycle_config['targetVariable'],
            overwrite=True
            )
    # init the feature space for the active search
    data.feature_space(scaling=True)

    # -
    # number of new points to sample
    new_batch = cycle_config['newBatch']

    if cycle_config['cycleN'] == 0:

        print('Cycle 0 assumes no points are known and the search space is completely unexplored.')
        print('The information about the acquisition funciton and the classifier will be skipped.')
        assert cycle_config['validatedset'] is None, f'Cycle 0 was selected but a validation set was given.'\
                                                      'Please check the config.yaml'

        new_idxs_al = alclf.acquisition.sampling_fps(X=data.X, n=new_batch)

    elif cycle_config['cycleN'] > 0:

        print('\nSearching for new points in an active way ...')

        if cycle_config['cycleN'] > 1 and cycle_config['validatedset'] is None:
            raise ValueError('Validation dataframe not set, check config.yaml file!')
        # -
        # set up the classifier
        if cycle_config['kParam1'] and cycle_config['kParam2']:
            print(f'Kernel initialized with values: A={cycle_config['kParam1']}, B={cycle_config['kParam2']}')
            kernel_function = cycle_config['kParam1']*alclf.classification.RBF(cycle_config['kParam2'])
        else:
            print(f'Kernel initialized with dafault values: A=1.0, B=1.0')
            kernel_function = 1.0*alclf.classification.RBF(1.0)

        if cycle_config['clf_dict'] is not None:
            print(f'Additional clf settings: {cycle_config['clf_dict']}')

            classifier_func = alclf.ClassifierModel(model=cycle_config['clfModel'],
                                                    kernel=kernel_function,
                                                    random_state=cycle_config['rngSeed'],
                                                    **cycle_config['clf_dict'])
        else:
            classifier_func = alclf.ClassifierModel(model=cycle_config['clfModel'],
                                                    kernel=kernel_function,
                                                    random_state=cycle_config['rngSeed'])

        # -
        # set up the acquisition function

        acquisition_func = alclf.DecisionFunction(mode=cycle_config['acqMode'],
                                                  decimals=cycle_config['entropyDecimals'],
                                                  seed=cycle_config['rngSeed'])
        
        # - 
        # initialize the starting configuration
        # from the existing data
        known_idxs = data.y.index[data.y != -1].tolist()

        # - 
        # Active learning cycle
        new_idxs_al, points_pdf = active_learning_cycle(
            feature_space=(data.X, data.y),
            idxs=known_idxs,
            new_batch=new_batch,
            clfModel=classifier_func,
            acquisitionFunc=acquisition_func,
            screeningSelection=cycle_config['screeningSelection']
        )

    # -
    # add the bardcodes
    new_points_df, unique_keys = add_keyID_to_dataframe(df=data.df.iloc[new_idxs_al],
                                                        col_name='Barcode',
                                                        generator_mode='custom')
    
    assert len(unique_keys) == len(set(unique_keys)), f"Error: keys were non uniquely generated!"

    print('\nNew points to validate:')
    print(new_points_df)

    barcode_df = new_points_df['Barcode']
    
    # -
    # end of cycle saving variables
    output_name = f'{cycle_config['experimentID']}_cycle{cycle_config['cycleN']}'
    # saving files
    new_points_df.to_csv(output_name+f'_ouput_points.csv', index=False)

    np.savetxt(output_name+f'_ouput_points.ndx', new_points_df.index.tolist())

    if cycle_config['cycleN'] > 0:
        np.save(output_name+f'_ouput_points_pdf.npy', points_pdf)

    barcode_df.to_csv(output_name+f'_ouput_barcodes.csv', index=False)

    if cycle_config['cycleN'] > 0:
        joblib.dump(classifier_func.clf, output_name+f'_ouput_algorithm.pkl')

    print(f'\n# End of Cycle {cycle_config['cycleN']}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='config', required=True, type=str, help='Cycle configuration (.yaml file).')
    args = parser.parse_args()
    main(argument=args)