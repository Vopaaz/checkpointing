import numpy as np
from checkpointing.hash.primitives import hash_bytes


def hash_numpy_array(obj: np.ndarray, algorithm: str = None) -> str:
    bytes_data = obj.tobytes(order="C")
    return hash_bytes(bytes_data, algorithm=algorithm)
