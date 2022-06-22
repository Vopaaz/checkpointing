"""
The checkpointing.hash module is structured as follows:

The submodules under this module, such as checkpointing.hash.primitives, checkpointing.hash._numpy, etc.,
implements functions that gets the optimized binary representation of certain objects, and update a given
hashlib._Hash instance. These methods are intended for in-module use only.

>>> import hashlib
>>> from checkpointing.hash.primitives import hash_bytes
>>> base = hashlib.md5()
>>> hash_bytes(base, b'abc').hexdigest()
'900150983cd24fb0d6963f7d28e17f72'

checkpointing.hash._typing is an exception. It only provides a typing analog of hashlib._Hash, which cannot
be used directly.

In this `__init__.py`, a `hash_anything` function is defined for other modules to use.
See its docstring for detailed information.
"""

import sys
from typing import Any
from collections import defaultdict
from checkpointing.hash.primitives import hash_object
from checkpointing.config import defaults
import pickle
import hashlib
from importlib.util import find_spec

def is_installed(module_name):
    return find_spec(module_name)

hashers = {}
"""
Mapping of object classes to their corresponding hash functions implemented in the submodules.
If a specific function does not exists, fallbacks to checkpointing.hash.primitives.hash_object
"""

if is_installed("numpy"):
    import numpy as np
    from checkpointing.hash._numpy import hash_numpy_array

    hashers[np.ndarray] = hash_numpy_array


if is_installed("pandas"):
    import pandas as pd
    from checkpointing.hash._pandas import hash_pandas_object

    hashers[pd.Series] = hash_pandas_object
    hashers[pd.DataFrame] = hash_pandas_object


def hash_anything(*objs: Any, algorithm=None, pickle_protocol: int=pickle.DEFAULT_PROTOCOL) -> str:
    """
    Args:
        objs: the objects to be hashed
        algorithm: the hash algorithm. If it's not specified, use the default in the global configuration (`defaults["hash.algorithm"]`)
        pickle_protocol: the pickle protocol to use for hashing objects that does not have an optimized hasher, 
                            and thus using the pickle_based fallback hasher

    Returns: a hexdigest of the hash value

    >>> hash_anything(0, "hello", [1, {"a": "b"}], pickle_protocol=3)
    '656b476a9f8fb668107c756113b38d89'
    """

    if algorithm is None:
        algorithm = defaults["hash.algorithm"]

    hash_base = hashlib.new(algorithm)

    for obj in objs:
        if type(obj) in hashers:
            hash_fn = hashers[type(obj)]
            hash_fn(hash_base, obj)
        else:
            hash_object(hash_base, obj, pickle_protocol)

    return hash_base.hexdigest()
