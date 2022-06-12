from typing import Any
from checkpointing.config import defaults
import hashlib
import pickle


def hash_bytes(*bytes_: bytes, algorithm: str = None) -> str:
    """
    Hash the bytes with the given algorithm.
    The algorithm must be a valid value supported by `hashlib`, and must be provided as a keyword argument.
    If it's not specified, use the default in the global configuration (`defaults["hash.algorithm"]`)

    >>> res = hash_bytes(b'abc', b'def', algorithm="md5")
    >>> ref = hashlib.new("md5").update(b'abc').update(b'def').hexdigest()
    >>> res == ref
    True
    """

    if algorithm is None:
        algorithm = defaults["hash.algorithm"]

    hash_fn = hashlib.new(algorithm)
    for byte in bytes_:
        hash_fn.update(byte)

    return hash_fn.hexdigest()


def hash_object(obj: Any, algorithm: str = None, pickle_protocol=pickle.DEFAULT_PROTOCOL) -> bytes:
    """
    Hash the given object by getting it's binary representation as if it gets dumped with pickle,
    and hash the `bytes` object with the given algorithm.

    Args:
        obj: the object to hash
        algorithm: the hash algorithm to use
        pickle_protocol: the pickle protocol to use
    """

    bytes_ = pickle.dumps(obj, protocol=pickle_protocol)
    return hash_bytes(bytes_, algorithm=algorithm)
