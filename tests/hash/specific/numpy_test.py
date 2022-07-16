from checkpointing.hash import hash_anything
import numpy as np


def test_hash_same_numpy_array():
    a = np.array([1, 2, 3])
    b = np.array([1, 2, 3])
    assert hash_anything(a) == hash_anything(b)


def test_hash_different_numpy_array():
    a = np.array([1, 2, 3])
    b = np.array([1, 2, 4])
    assert hash_anything(a) != hash_anything(b)
