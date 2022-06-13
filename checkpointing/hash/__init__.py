"""
The checkpointing.hash module is structured as follows:

The submodules under this module, such as checkpointing.hash.primitives, checkpointing.hash._numpy, etc.,
implements functions that gets the optimized binary representation of certain objects, and update a given
hashlib._Hash instance. These methods are intended for in-module use only.

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
import hashlib

hashers = defaultdict(lambda: hash_object)
"""
Mapping of object classes to their corresponding hash functions implemented in the submodules.
If a specific function does not exists, fallbacks to checkpointing.hash.primitives.hash_object
"""

if "numpy" in sys.modules:
    import numpy as np
    from checkpointing.hash._numpy import hash_numpy_array

    hashers[np.ndarray] = hash_numpy_array


if "pandas" in sys.modules:
    import pandas as pd
    from checkpointing.hash._pandas import hash_pandas_object

    hashers[pd.Series] = hash_pandas_object
    hashers[pd.DataFrame] = hash_pandas_object


def hash_anything(*objs: Any, algorithm=None) -> str:
    """
    """

    if algorithm is None:
        algorithm = defaults["hash.algorithm"]

    hash_base = hashlib.new(algorithm)

    for obj in objs:
        hash_fn = hashers[type(obj)]
        hash_fn(hash_base, obj)

    return hash_base.hexdigest()
