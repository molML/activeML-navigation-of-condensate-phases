#!

import argparse
import pandas as pd
from robotexperiments.manager import fileManager, get_files_from, select_first_item_with_pattern
from robotexperiments.formats import FOLDERS_TREE

FILE_PATTERN = 'ouput_points'

# - MAIN 

def main(arguments):
    # -----------------------------------
    # - env variables
    EXP_FOLDER = FOLDERS_TREE['experiments'][arguments.expID]
    CYCLE_FOLDER = f'cycles/cycle_{arguments.ncycle}/'

    # -----------------------------------
    # - init the fileManager
    manager = fileManager()

    # -----------------------------------
    # - read output files
    output_csv_files = get_files_from(folder=EXP_FOLDER+CYCLE_FOLDER, ew='.csv', verbose=False)

    # -----------------------------------
    # - append to master file
    output_points_csv = select_first_item_with_pattern(strings=output_csv_files, 
                                                       pattern=FILE_PATTERN)

    print(f'Output file with not validated points to be appended:\n{output_points_csv}')
    output_points_df = pd.read_csv(EXP_FOLDER+CYCLE_FOLDER+output_points_csv)

    manager.append_data(new_data=output_points_df, fill_value=0)

    # - saving to new version
    manager.save_file(overwrite=False)

    print('# END')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-expID', dest='expID', required=True, type=str, help='Experiment ID (as for the folders tree)')
    parser.add_argument('-ncycle', dest='ncycle', required=True, type=str, help='Cycle number.')
    args = parser.parse_args()
    main(arguments=args)

