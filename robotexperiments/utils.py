# -------------------------------------------------- #
# Utility functions
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import json
import toml
import random
import string
import time
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
from scipy.spatial import distance
from types import SimpleNamespace
from typing import Union, List, Tuple

# -------------------------------------------------- #
# --- JSD

def js_divergence(p, q):
    # Convert to numpy arrays
    p = np.array(p)
    q = np.array(q)
    
    # Add a small value to avoid log(0)
    epsilon = 1e-10
    p = np.clip(p, epsilon, 1)
    q = np.clip(q, epsilon, 1)
    
    # Compute JSD
    jsd = distance.jensenshannon(p, q)
    
    return jsd


def js_divergence_classwise(p, q):
    # Compare Class 0
    jsd_class0 = js_divergence(p[:, 0], q[:, 0])
    
    # Compare Class 1
    jsd_class1 = js_divergence(p[:, 1], q[:, 1])
    
    return jsd_class0, jsd_class1


def js_divergence_matrix(p, q):
    # Ensure input arrays are numpy arrays
    p = np.array(p)
    q = np.array(q)
    
    # Add a small value to avoid log(0)
    epsilon = 1e-10
    p = np.clip(p, epsilon, 1)
    q = np.clip(q, epsilon, 1)
    
    # Normalize row-wise to ensure they are valid probability distributions
    p = p / p.sum(axis=1, keepdims=True)
    q = q / q.sum(axis=1, keepdims=True)
    
    # Calculate row-wise JSD
    jsd_values = np.array([distance.jensenshannon(p[i], q[i]) for i in range(p.shape[0])])
    
    # Return the mean JSD across all rows
    return np.mean(jsd_values)


# -------------------------------------------------- #
# --- custom exception

class WrongConfigFormat(Exception):
    pass


# -------------------------------------------------- #
# --- parse dict file .json .toml

def parse_config(filename: str, 
                 toNameSpace: bool =False) -> dict:
    """Parse a file with the .json or .toml extension
    to a py dictionary.

    :param filename: file absolute path.
    :type filename: str
    :param toNameSpace: return Namespace, defaults to False
    :type toNameSpace: bool, optional
    :raises WrongConfigFormat: wrong file extension.
    :return: parsed dictionary.
    :rtype: dict
    """
    with open(filename, 'r') as f:
        if filename.endswith('.json'):
            _config = json.load(f)
        elif filename.endswith('.toml'):
            _config = toml.load(f)
        else:
            raise WrongConfigFormat(
                f"Format of the '{filename}' is not supported. "
                "Available formats: .json, .toml"
            )
        if toNameSpace:
            return SimpleNamespace(**_config)
        else:
            return _config
        

# -------------------------------------------------- #
# --- save dict to file .json

def save_to_jason(dictonary: dict, fout_name: str) -> None:
    timestamp = datetime.now().strftime('%b_%d_%Y-%H:%M:%S')
    dictonary['execution'] = timestamp
    with open(fout_name+'.json', 'w', encoding='utf-8') as f:
        json.dump(dictonary, 
                  f, 
                  ensure_ascii=False, 
                  indent=4)
        

# -------------------------------------------------- #
# --- custom key labeling encoding

def generate_key(mode: str='custom') -> str:

    ALLOW_MODES = ['custom', 'uuid_c']

    assert mode in ALLOW_MODES, f"Specified 'mode' not available. " \
                                f"Select from: {ALLOW_MODES}"

    if mode == 'custom':
        timestamp = ''.join(random.choices(str(int(time.time())), k=6))
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{timestamp}{random_chars}"
    
    elif mode == 'uuid_c':
        return str(uuid.uuid4()).split(sep='-')[-1]
    

def add_keyID_to_dataframe(df: pd.DataFrame, 
                           col_name: str='Barcode',
                           generator_mode='custom') -> Tuple[pd.DataFrame, List]:
    
    n_keys = len(df)
    keys_id = list()
    for i in range(n_keys):
        keys_id.append(generate_key(mode=generator_mode))

    df.insert(len(df.columns), col_name, keys_id)

    return df, keys_id