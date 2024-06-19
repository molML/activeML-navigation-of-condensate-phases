#!

import os
import re
from typing import List, Union
import pandas as pd
from .formats import MASTER_FILE_COLUMNS, FOLDERS_TREE, MASTER_FILE_NAME_FORMAT

# -- FUNCTIONS

# -------------------------------------------------- #
# --- file and folders handling

def atoi(text: str) -> str:
    return int(text) if text.isdigit() else text


def natural_keys(text: str) -> List[str]:
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def get_files_from(folder: str, 
                   ew: str=None, 
                   sw: str=None, 
                   verbose: bool=True) -> List[str]:
    """Simple function to select files from a location
    with possible restraints.
    folder : file str location
    ew : "endswith" str selection
    sw : "startswith" str selection
    """
    file_list = list()
    # file selection following the constraints
    for entry in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, entry)):
            if ew:
                if entry.endswith(ew):
                    file_list.append(entry)
            elif sw:
                if entry.startswith(sw):
                    file_list.append(entry)
            else:
                file_list.append(entry)
    # sorting of the files :)
    file_list.sort(key=natural_keys)
    if verbose:
        print(f"Files:\n{file_list}, ({len(file_list)})")
    return file_list


def filter_rows_by_values(df: pd.DataFrame, 
                          column_name: str, 
                          values: List[str]) -> pd.DataFrame:
    """
    Filters rows in the DataFrame where the specified column has values in the provided list.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    column_name (str): The column name to filter by.
    values (list): List of values to filter by.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    return df[df[column_name].isin(values)]


def select_first_item_with_pattern(strings: List[str], pattern: str):
    """
    Selects the first item from a list of strings that contains a specific pattern.

    Parameters:
    strings (list): List of strings to filter.
    pattern (str): The pattern to search for.

    Returns:
    str or None: The first string that contains the pattern, or None if no match is found.
    """
    for s in strings:
        if pattern in s:
            return s
    return None


# -- OBJECTS

class fileManager:

    def __init__(self, 
                 df_columns: List[str]=MASTER_FILE_COLUMNS,
                 file_name_format: str=MASTER_FILE_NAME_FORMAT,
                 folders_tree: dict=FOLDERS_TREE) -> None:
        
        self.master_columns = df_columns
        self.master_file_name_format = file_name_format

        self.folders_tree = folders_tree
        
        # check for the existence of masterfile
        print('Checking for master files ...')
        self.master_folder = get_files_from(folder=self.folders_tree['master_file'], 
                                            verbose=False)
        print(f'Master files found:\n{self.master_folder}')

        if len(self.master_folder) == 0:
            print('Creating new master file')
            self.master_df = pd.DataFrame(columns=self.master_columns)
            self.master_file = self.master_file_name_format.format(len(self.master_folder))
            self.master_df.to_csv(
                self.folders_tree['master_file']+self.master_file,
                index=False)
            print(self.master_df)
        
        else:
            print(f'Selecting last version: {self.master_folder[-1]}')
            self.master_file = self.master_folder[-1]
            self.master_df = pd.read_csv(self.folders_tree['master_file']+self.master_file)
            print(self.master_df.tail(10))

        self.master_file_version = len(self.master_folder)
        pass

    
    def append_data(self, new_data: pd.DataFrame, fill_value: Union[int,float,str]=None):
        # Identify new columns that are not in the DataFrame
        new_columns = set(new_data.keys()) - set(self.master_df.columns)
        print(f'Found new columns: {len(new_columns)}')
        if len(new_columns) > 0:
            print(f'New columns: {new_columns}')
            print(f'The columns will be added and values set to: {fill_value}')
        else:
            pass
        # Add new columns to the DataFrame
        self.master_df = pd.concat([self.master_df, new_data], ignore_index=True)

        # fill in the blanks converting NaN to user defined value
        if fill_value is not None:
            self.master_df = self.master_df.fillna(fill_value)
        pass
    

    def update_data_values(self, 
                           updated_data: pd.DataFrame,
                           reference_key: str='barcode') -> None:
        reference_values = self.master_df[reference_key].values
        # Merge the updated DataFrames using the reference key as support 
        df_updated = self.master_df.merge(updated_data, 
                                          on=reference_key, 
                                          how='left', 
                                          suffixes=('', '_new')
                                          )
        
        # Update the original columns with the new values
        updated_cols = [col for col in updated_data.columns if col != reference_key]
        for col in updated_cols:
            df_updated[col] = df_updated[col + '_new'].combine_first(df_updated[col])

        # Drop the temporary new columns
        df_updated = df_updated.drop(columns=[col + '_new' for col in updated_cols])

        # substitue the updated master dataframe with the updated one
        print('Updated data values:\n')
        _old_df_tmp = filter_rows_by_values(df=self.master_df, 
                                            column_name=reference_key,
                                            values=reference_values)
        print(f'OLD:\n{_old_df_tmp}')
        _new_df_tmp = filter_rows_by_values(df=df_updated, 
                                            column_name=reference_key,
                                            values=reference_values)
        print(f'NEW (updated):\n{_new_df_tmp}')
        self.master_df = df_updated
        pass


    def save_file(self, overwrite: bool=False) -> None:
        if not overwrite:
            save_file_name = self.folders_tree['master_file']+self.master_file_name_format.format(self.master_file_version)
            assert save_file_name not in self.master_folder, f'File name identical to one already saved!'
            print(f'New file saved: {save_file_name}')
        elif overwrite:
            save_file_name = self.folders_tree['master_file']+self.master_file_name_format.format(self.master_file_version-1)
            print(f'File saved & overwritten on {save_file_name}')
        self.master_df.to_csv(save_file_name, index=False,)
        pass

