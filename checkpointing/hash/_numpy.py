import numpy as np
from checkpointing.hash.default import hash_bytes

def hash_numpy_array(obj: np.ndarray):
    bytes_data = obj.tobytes(order="C")

