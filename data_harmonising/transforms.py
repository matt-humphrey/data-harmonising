# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_transforms.ipynb.

# %% auto 0
__all__ = ['apply_conditions', 'create_variables_with_conditions', 'reformat_create', 'create_variables', 'rename_variables',
           'delete_variables', 'reformat_crud']

# %% ../nbs/02_transforms.ipynb 3
from fastcore.utils import *
import pandas as pd
from pandas import DataFrame
import numpy as np
from typing import Dict, List, Tuple, Any

from .data import *

# %% ../nbs/02_transforms.ipynb 6
# TODO: broaden it so it also accepts multiple condition_cols; responds differently depending on list or str?
def apply_conditions(df: DataFrame, 
                     condition_col: str, 
                     conditions: List[Dict[str, Any]],
                     default = np.nan
                     ) -> np.ndarray:
    """Apply a series of conditions to a column and return the resulting values."""
    conditions_list = []
    choices = []

    for condition in conditions:
        cond = condition['condition']
        value = condition['value']
        
        if callable(cond):
            conditions_list.append(df[condition_col].apply(cond))
        else:
            conditions_list.append(df[condition_col] == cond)
        
        choices.append(value)
    
    return np.select(conditions_list, choices, default=default)

# %% ../nbs/02_transforms.ipynb 8
# TODO: decouple from apply_conditions; make separate/orthogonal such that functions can be composed sequentially
def create_variables_with_conditions(df: DataFrame, # 
                     meta: DataFrame, # 
                     transformations: List[Dict[str, Any]] #  
                     ) -> DataFrame: # 
    """Create new variables based on conditions and concatenate them to the DataFrame."""
    new_columns = {}

    for transformation in transformations:
        target_col = transformation['target_col']
        condition_col = transformation['condition_col']
        conditions = transformation['conditions']

        new_columns[target_col] = apply_conditions(df, condition_col, conditions)

    # Create a new DataFrame with the new columns
    new_df = DataFrame(new_columns, index=df.index)
    # Concatenate the new columns to the original DataFrame
    df = pd.concat([df, new_df], axis=1)

    new_columns = list(new_columns.keys())
    # Create new variables in metadata with no information (to later be harmonised)
    meta[new_columns] = np.nan

    return df, meta

# %% ../nbs/02_transforms.ipynb 10
def reformat_create(create: List[Dict[str, Any]] # variables to be created
                    ) -> List[str]:
    return [col['target_col'] for col in create]

# %% ../nbs/02_transforms.ipynb 12
def create_variables(df: DataFrame, # data
                     meta: DataFrame, # metadata
                     vars: List[str] # list of variables to remove
                     ) -> DataFrame:
    df = df.assign(**{col: pd.NA for col in vars})
    meta = meta.assign(**{col: pd.NA for col in vars})
    
    # Test variables were created
    assert set(vars).issubset(df.columns)
    assert set(vars).issubset(meta.columns)

    return df, meta

# %% ../nbs/02_transforms.ipynb 14
def rename_variables(df: DataFrame, # data
                     meta: DataFrame, # metadata
                     vars: Dict[str, str]
                     ) -> DataFrame:
    df = df.rename(columns=vars)
    meta = meta.rename(columns=vars)
    
    # Test changes successful
    for original, updated in vars.items():
        assert original not in df.columns
        assert original not in meta.columns
        assert updated in df.columns
        assert updated in meta.columns
    
    return df, meta

# %% ../nbs/02_transforms.ipynb 16
def delete_variables(df: DataFrame, # data
                     meta: DataFrame, # metadata
                     vars: List[str] # list of variables to remove
                     ) -> DataFrame:
    df = df.drop(vars, axis=1)
    meta = meta.drop(vars, axis=1)
    
    # Test variables have correctly been removed
    set(vars).isdisjoint(df.columns)
    set(vars).isdisjoint(meta.columns)

    return df, meta

# %% ../nbs/02_transforms.ipynb 18
def reformat_crud(create: List[Dict[str, Any]], # variables to be created
                  rename: Dict[str, str], # variables to be renamed
                  delete: List[str], # variables to be deleted
                  ) -> List[List[str]]:
    replaced = list(rename.keys())
    updated = list(rename.values())
    added = create + updated
    removed = delete + replaced
    return added, removed
