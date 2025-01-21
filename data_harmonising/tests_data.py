# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_tests_data.ipynb.

# %% auto 0
__all__ = ['test_columns', 'verify_change', 'verify_changes', 'filter_updated_for_comparison', 'filter_original_for_comparison',
           'columns_with_data_changed', 'test_data_eq', 'verify_data_unchanged_for_unchanged_columns',
           'verify_data_unchanged_for_changed_columns', 'test_data_created', 'run_full_test_suite']

# %% ../nbs/03_tests_data.ipynb 3
from fastcore.utils import *
import pandas as pd
from pandas import DataFrame
import numpy as np
from typing import Dict, List, Tuple, Any

from .data import *
from .transforms import *

import raine_tools as rn

# %% ../nbs/03_tests_data.ipynb 21
def test_columns(df1: DataFrame, # updated raw data
                 df2: DataFrame, # original raw data
                 added: List[str], # variables to be created
                 removed: List[str], # old variables that were renamed
                 ) -> None:
    """Verify only intended changes were made to columns."""
    unchanged = [col for col in df2.columns if col not in removed]

    # Check all columns to be added exist
    assert all([col in df1.columns for col in added])
    # Check all columns to be removed do not exist
    assert all([col not in df1.columns for col in removed])
    # Check all other columns exist
    assert all([col in df1.columns for col in unchanged])

# %% ../nbs/03_tests_data.ipynb 24
def verify_change(df: DataFrame, # updated dataset
                  columns: List[str], # columns impacted
                  idx: List[int], # IDs impacted
                  value: int|str # new value
                   ) -> None:
    """Verify that for corresponding columns and IDs specified, these changes were implemented."""
    assert np.all(df.loc[idx, columns] == value)

def verify_changes(df: DataFrame, # updated dataset
                   changes: List[Dict[str, Any]], # explicit changes
                   ) -> None: 
    """Run `verify_change` for each change specified in `changes` for the given dataframe."""
    for change in changes:
        columns = change["columns"]
        idx = change["idx"]
        value = change["value"]
        verify_change(df, columns, idx, value)

# %% ../nbs/03_tests_data.ipynb 35
def filter_updated_for_comparison(df: DataFrame, # updated raw data
                                  create: List[Dict[str, Any]], # variables to be created
                                  ) -> DataFrame:
    """Filter out newly added variables."""
    created = reformat_create(create)
    return df[df.columns.difference(created, sort=False)]

def filter_original_for_comparison(df: DataFrame, # original raw data
                                   rename: Dict[str, str], # variables to be renamed
                                   delete: List[str], # variables to be deleted
                                   ) -> DataFrame:
    """Filter out deleted variables, and rename old variables for comparison."""
    return df[df.columns.difference(delete, sort=False)].rename(columns=rename)

# %% ../nbs/03_tests_data.ipynb 36
def columns_with_data_changed(changes: List[Dict[str, Any]] # explicit changes
                              ) -> List[str]:
    """Return a list of unique columns where data was changed."""
    return list({col for change in changes for col in change['columns']})

# %% ../nbs/03_tests_data.ipynb 37
def test_data_eq(df1: DataFrame, # updated raw data
                 df2: DataFrame, # original raw data
                 ) -> None:
    """Verify two datasets are the same."""
    pd.testing.assert_frame_equal(df1, df2)

def verify_data_unchanged_for_unchanged_columns(df1: DataFrame, # updated raw data
                                                df2: DataFrame, # original raw data
                                                changes: List[Dict[str, Any]] # explicit changes
                                                ) -> None:
    """Verify the updated and original datasets remain unchanged except for all columns where no changes were implemented."""
    changed_columns = columns_with_data_changed(changes)
    df1 = df1.drop(columns=changed_columns)
    df2 = df2.drop(columns=changed_columns)
    test_data_eq(df1, df2)

# %% ../nbs/03_tests_data.ipynb 41
def verify_data_unchanged_for_changed_columns(df1: DataFrame, # updated raw data
                                              df2: DataFrame, # original raw data
                                              changes: List[Dict[str, Any]] # explicit changes
                                              ) -> None:
    """Verify data remains identical for columns impacted by recoding for all IDs where no changes were implemented."""
    # Create a mask for changed cells
    mask = pd.DataFrame(False, index=df1.index, columns=df1.columns)

    for change in changes:
        for col in change['columns']:
            mask.loc[change['idx'], col] = True

    test_data_eq(df1[~mask], df2[~mask])

# %% ../nbs/03_tests_data.ipynb 45
def test_data_created():
    """Verify that columns that were created..."""
    pass

# %% ../nbs/03_tests_data.ipynb 46
def run_full_test_suite(df1: DataFrame, # updated raw data
                        df2: DataFrame, # original raw data
                        create: List[Dict[str, Any]], # variables to be created
                        rename: Dict[str, str], # variables to be renamed
                        delete: List[str], # variables to be deleted
                        changes: List[Dict[str, Any]] # explicit changes
                        ) -> None:
    """Run all tests for validating data."""
    # Filter for matching columns to compare
    df1_filtered = filter_updated_for_comparison(df1, create)
    df2_filtered = filter_original_for_comparison(df2, rename, delete)

    added, removed = reformat_crud(create, rename, delete)

    # Validate columns
    test_columns(df1, df2, added, removed)

    # Validate raw data, not including variables that were created or deleted, and renaming the old variables to match for comparison
    verify_changes(df1, changes)

    # Confirm all data remains identical for columns that were not intended for change
    verify_data_unchanged_for_unchanged_columns(df1_filtered, df2_filtered, changes)

    # Confirm that for columns where changes were implemented, data remains the same for all IDs where no changes were intended
    verify_data_unchanged_for_changed_columns(df1_filtered, df2_filtered, changes)

    print("All tests run successfully.")
