#!

import argparse
import pandas as pd
from robotexperiments.fileManager import MasterFileManager, get_files_from, select_first_item_with_pattern
from robotexperiments.formats import FOLDERS_TREE

FILE_PATTERN = 'validated_points'

# - MAIN 

def main(arguments):
    # -----------------------------------
    # - env variables
    EXP_FOLDER = FOLDERS_TREE['experiments'][arguments.expID]
    CYCLE_FOLDER = f'cycles/cycle_{arguments.ncycle}/'

    # -----------------------------------
    # - init the MasterFileManager
    manager = MasterFileManager()

    # -----------------------------------
    # - read output files
    output_csv_files = get_files_from(folder=EXP_FOLDER+CYCLE_FOLDER, ew='.csv', verbose=False)

    # -----------------------------------
    # - append to master file
    print('\nUpdate master file with validated points mode selected.')
    validated_points_csv = select_first_item_with_pattern(strings=output_csv_files,
                                                          pattern=FILE_PATTERN)

    print(f'Output file with validated points:\n{validated_points_csv}')
    validated_points_df = pd.read_csv(EXP_FOLDER+CYCLE_FOLDER+validated_points_csv)

    manager.update_data_values(updated_data=validated_points_df,
                               reference_key=arguments.reference)
    
    # - saving
    manager.save_file(overwrite=True)

    print('# END')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-expID', dest='expID', required=True, type=str, help='Experiment ID (as for the folders tree)')
    parser.add_argument('-ncycle', dest='ncycle', required=True, type=str, help='Cycle number.')
    parser.add_argument('-reference', dest='reference', default='Barcode', type=str, help='Reference column key for the update.')
    args = parser.parse_args()
    main(arguments=args)


