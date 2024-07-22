# -------------------------------------------------- #
# Script for initializing the Desing space of the 
# experiments
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import argparse
import pandas as pd

import robotexperiments.dataManager as dm
from robotexperiments.utils import parse_config, save_to_jason

# --- global configs

KEYS_PD_VAR = ['Experiment_ID', 'phase_diagram_variables']

# --- Main

def main(arguments):

    # parse the experiment config
    expvar_config = parse_config(filename=arguments.phasevar)

    assert all(key in KEYS_PD_VAR for key in expvar_config.keys()), \
    f"Please structure the `.json` file as provided by the example."\
    f"The keys do not match the requirements ({KEYS_PD_VAR})."

    # read the provided existing experiments
    if arguments.dfcsv:
        existing_df = pd.read_csv(arguments.dfcsv)
    
        assert all(key in existing_df.columns for key in expvar_config['phase_diagram_variables'].keys()), \
        f"Please structure the `.json` file as provided by the example."\
        f"The keys of the csv profivede don't match the keys in the .json file."
        # create the DoE dataframe
        doe_df = dm.create_experimental_design(ranges_dict=expvar_config['phase_diagram_variables'], 
                                               existing_evidences_df=existing_df,
                                               target_property='Phase')
    else:
        # create the DoE dataframe
        doe_df = dm.create_experimental_design(ranges_dict=expvar_config['phase_diagram_variables'], 
                                               existing_evidences_df=None, 
                                               target_property='Phase')
        print('\nNo exisitng dataframe with experiment provided.\n')
    
    # create the static dataframe with the experiment information
    if arguments.sysvar:
        sysvar_config = parse_config(filename=arguments.sysvar)
        static_df = dm.create_system_variables_df(input_dict=sysvar_config)

    # saving files
    experiment_name = expvar_config['Experiment_ID']+f'_{str(len(expvar_config['phase_diagram_variables'].keys())-1)}Dim.csv'

    if arguments.dir:
        save_dir = arguments.dir+'/'
    else:
        save_dir = './'

    doe_df.to_csv(save_dir+"DOE_"+experiment_name, index=False)
    print("Saving DoE dataframe ...")
    print(doe_df.head())
    print(":\t:\t:\t:\t:\t:")
    print(doe_df.tail())

    if arguments.sysvar:
        static_df.to_csv(save_dir+"STATIC_"+experiment_name, index=False)
        print("\nSaving static experiment information ...")
        print(static_df.head())

    save_to_jason(dictonary=expvar_config,
                  fout_name=save_dir+'exp_phasevar_config_file.json')    

    print('\n# END')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-phasevar', dest='phasevar', required=True, type=str, help='Config file for the phase diagram variables.')
    parser.add_argument('-sysvar', dest='sysvar', default=None, type=str, help='Config file for the experiment system variables.')
    parser.add_argument('-dfcsv', dest='dfcsv', default=None, help='Existing df in .csv extension.')
    parser.add_argument('-dir', dest='dir', default=None, help='Directory where to save files.')
    args = parser.parse_args()
    main(arguments=args)