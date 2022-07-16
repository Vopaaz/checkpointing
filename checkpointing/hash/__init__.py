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
        pickle_protocol: the pickle protocol to use for hashing objects that does not have an
                         specific hasher, and thus using the pickle based fallback hasher.
                         If it's not specified, user the global default `hash.pickle_protocol`

    Returns: a hexdigest of the hash value

    >>> hash_anything(0, "hello", [1, {"a": "b"}], pickle_protocol=3)
    '656b476a9f8fb668107c756113b38d89'

    Note that when hashing some objects, such as functions, lambdas, generators, etc, it only
    hashes the reference to their definition.  This could result in unexpected behaviors leading
    to incorrect equality comparison.

    >>> def foo():
    ...     for i in range(10):
    ...         yield i
    >>>
    >>> f1 = foo()
    >>> f2 = foo()
    >>> next(f2) # Now the state of f1 and f2 are different
    0
    >>> hash_anything(f1) == hash_anything(f2) # But they are refere
    True
    """

    if algorithm is None:
        algorithm = defaults["hash.algorithm"]

    if pickle_protocol is None:
        pickle_protocol = defaults["hash.pickle_protocol"]

    hash_base = hashlib.new(algorithm)

    for obj in objs:

        if hashable_with_specific(obj):
            bytes_ = hash_with_specific(obj)

        else:
            bytes_ = hash_generic(obj, pickle_protocol)

        hash_base.update(bytes_)

    return hash_base.hexdigest()
