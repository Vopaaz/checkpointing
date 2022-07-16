from importlib.util import find_spec
from typing import Any, Callable
from checkpointing.hash._typing import Hash
from checkpointing.exceptions import HashFailedError
from checkpointing.hash.specific._numpy import hash_numpy_array
from checkpointing.hash.specific._pandas import hash_pandas_object


def is_installed(module_name):
    return find_spec(module_name) is not None


hashers = {}
"""
Mapping of object classes to their corresponding hash functions implemented in the submodules.
If a specific function does not exists, fallbacks to checkpointing.hash.primitives.hash_object
"""

if is_installed("numpy"):
    import numpy as np
    from checkpointing.hash.specific._numpy import hash_numpy_array

    hashers[np.ndarray] = hash_numpy_array


if is_installed("pandas"):
    import pandas as pd
    from checkpointing.hash.specific._pandas import hash_pandas_object

    hashers[pd.Series] = hash_pandas_object
    hashers[pd.DataFrame] = hash_pandas_object


def register_hasher(class_: Any, hasher: Callable):
    hashers[class_] = hasher


def hash_with_specific(obj: Any):
    if type(obj) in hashers:
        hash_fn = hashers[type(obj)]
        return hash_fn(obj)
    else:
        raise HashFailedError(f"No registered hasher found for type: {type(obj)}")


def hashable_with_specific(obj: Any):
    return type(obj) in hashers
