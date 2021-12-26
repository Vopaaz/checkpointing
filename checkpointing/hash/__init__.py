import sys
from collections import defaultdict
from checkpointing.hash.default import hash_object

hashers = defaultdict(lambda: hash_object)

if "numpy" in sys.modules:
    import numpy as np
    from checkpointing.hash._numpy import hash_numpy_array

    hashers[np.ndarray] = hash_numpy_array


if "pandas" in sys.modules:
    import pandas as pd
    from checkpointing.hash import _pandas
