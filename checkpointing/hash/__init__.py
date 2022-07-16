from typing import Any
from checkpointing.hash.generic import hash_generic
from checkpointing.hash.specific import hash_with_specific, hashable_with_specific
from checkpointing.config import defaults
import hashlib


def hash_anything(*objs: Any, algorithm: str = None, pickle_protocol: int = None) -> str:
    """
    Args:
        objs: the objects to be hashed
        algorithm: the hash algorithm. Must be supported by the hashlib.
                   If it's not specified, use the global default `hash.algorithm`.
        pickle_protocol: the pickle protocol to use for hashing objects that does not have an optimized hasher,
                         and thus using the pickle_based fallback hasher.
                         If it's not specified, user the global default `hash.pickle_protocol`

    Returns: a hexdigest of the hash value

    >>> hash_anything(0, "hello", [1, {"a": "b"}], pickle_protocol=3)
    '656b476a9f8fb668107c756113b38d89'
    """

    if algorithm is None:
        algorithm = defaults["hash.algorithm"]

    if pickle_protocol is None:
        pickle_protocol = defaults["hash.pickle_protocol"]

    hash_base = hashlib.new(algorithm)

    for obj in objs:

        if hashable_with_specific(obj):
            hash_with_specific(hash_base, obj)

        else:
            hash_generic(hash_base, obj, pickle_protocol)

    return hash_base.hexdigest()
