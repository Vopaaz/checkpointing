from typing import Any
from checkpointing.config import Config as config
import hashlib


def hash_bytes(algorithm: str = None, *bytes_: bytes) -> str:
    """
    Hash the bytes with the given algorithm.
    The algorithm must be a valid value supported by `hashlib`.

    >>> res = hash_bytes("md5", b'abc')
    >>> ref = hashlib.new("md5").update(b'abc').hexdigest()
    >>> res == ref
    True
    """
    if algorithm is None:
        algorithm = config.hash.algorithm

    hash_fn = hashlib.new(algorithm)
    for byte in bytes_:
        hash_fn.update(byte)

    return hash_fn.hexdigest()


def hash_object(obj: Any):
    pass
