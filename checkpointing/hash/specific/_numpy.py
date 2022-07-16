import numpy as np
from checkpointing.hash._typing import Hash

def hash_numpy_array(arr: np.ndarray) -> bytes:
    return arr.tobytes(order="C")
