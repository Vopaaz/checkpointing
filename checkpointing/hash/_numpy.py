import numpy as np
from checkpointing.hash._typing import Hash

def hash_numpy_array(hash_base: Hash, arr: np.ndarray) -> Hash:
    arr_bytes = arr.tobytes(order="C")
    return hash_base.update(arr_bytes)
