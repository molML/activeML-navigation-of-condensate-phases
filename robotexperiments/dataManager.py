# -------------------------------------------------- #
# Helper functions to handle the creation of the
# experimental pool of points for the Coacervate
# optimization experiments.
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import pandas as pd
import numpy as np

from typing import List, Union

# -------------------------------------------------- #
# --- create the inial DOE dataframe from input dict

def create_experimental_design(ranges_dict: dict, 
                               target_property: str="Phase",
                               existing_evidences_df: pd.DataFrame=None) -> pd.DataFrame:
    
    # assert that the `target_proerty` exists in the `input_dict`
    assert target_property in ranges_dict.keys(), f"Target ({target_property}) key not in `init_dict`"

    # init variables
    df = pd.DataFrame(columns=ranges_dict.keys())
    df_val_list = list()

    # init the ranges for the variable exploration
    for _, arg in ranges_dict.items():
        if isinstance(arg, list):
            df_val_list.append(arg)
        elif isinstance(arg, dict):
            assert all(karg in ['start', 'end', 'ev'] for karg in arg.keys()), f"Keys for the interval definition has to be {['start', 'end', 'ev']}"
            df_val_list.append(np.around(np.arange(arg['start'], arg['end'], arg['ev']), decimals=2))

    # create the meshgrid of points and recovers the
    # individual dimensions
    df_points_list = recover_points(
        create_meshgrid(arrays=df_val_list))
    
    # store all the values in the dataframe
    for col,val in zip(df.columns, df_points_list):
        df[col] = val
    df[target_property] = [ranges_dict[target_property]]*len(df)

    # if provided adds already existing data, dropping the duplicates
    if existing_evidences_df is not None:
        print(f'Adding existing {target_property}-diagram information')
        df = df_merger(df1=existing_evidences_df, df2=df, 
                       target_col=target_property, keep='first')

    return df


def create_meshgrid(arrays: List[np.ndarray]) -> np.ndarray:
    grid = np.meshgrid(*arrays)
    return np.asarray(grid)


def recover_points(meshgrid: np.ndarray) -> np.ndarray:
    num_dim = len(meshgrid)
    num_points = meshgrid[0].size
    positions = np.empty((num_dim, num_points), dtype=meshgrid[0].dtype)

    for i in range(num_dim):
        positions[i] = meshgrid[i].ravel()
    
    return positions


def df_merger(df1: pd.DataFrame, 
              df2: pd.DataFrame, 
              target_col: str='Phase', 
              keep: str='first',) -> pd.DataFrame:
    # stack the two df
    merged_df = pd.concat([df1, df2]).drop_duplicates(keep=keep).reset_index(drop=True)

    # remove the target columns, as it pollutes the duplicates
    target_column_df = merged_df[target_col]
    merged_df = merged_df.drop(columns=target_col, axis=1)

    # list of True: dup, False: uniq
    duplicates_list = merged_df.duplicated(keep='first')
    duplicates_indxs_list = np.arange(len(target_column_df))[duplicates_list]

    # add the target column back
    merged_df[target_col] = target_column_df

    return merged_df.drop(index=duplicates_indxs_list).reset_index(drop=True)

# -------------------------------------------------- #
# --- create the static dataframe from an input dictionary

def create_system_variables_df(input_dict: dict) -> pd.DataFrame:

    leveled_dict = dict()
    for key,arg in input_dict.items():
        if isinstance(arg, dict):
            sub_dict = subdictionary_merger(master_key=key,
                                            input_dict=arg)
            leveled_dict.update(sub_dict)
        else:
            leveled_dict[key] = arg

    return pd.DataFrame([leveled_dict])
    return leveled_dict


def subdictionary_merger(master_key: str,
                         input_dict: dict) -> dict:
    output_dict = dict()
    for key,arg in input_dict.items():
        new_key_str_tmp = master_key+'_'+key
        output_dict[new_key_str_tmp] = arg

    return output_dict

# -------------------------------------------------- #
# --- handle dataframes

def remove_columns(df: pd.DataFrame, 
                   key: Union[list[str], str]) -> pd.DataFrame:
    """
    Removes a column or a list of columns from a Dataframe.
    """
    try:
        if isinstance(key, list):
            to_drop = sum([[s for s in df.columns if k in s] for k in key], [])

        elif isinstance(key, str):
            to_drop = [s for s in df.columns if key in s]
            
    except:
        raise TypeError("Key parameters can only be `str` or `list`.")
    
    df = df.drop(labels=to_drop, 
                 axis=1)

    return df


def read_validated_df(df_path: str, 
                      remove_keys: Union[List[str], str]=None) -> pd.DataFrame:
    """
    Reads a validated DataFrames.
    The DF should contain all the variables neesed for the points search 
    plus the barcode identification and nothing else.
    """
    validated_df = pd.read_csv(df_path)
    if remove_keys:
        try:
            validated_df = remove_columns(df=validated_df, key=remove_keys)
        except:
            print(f'{remove_keys} already removed ..')
            
    return validated_df