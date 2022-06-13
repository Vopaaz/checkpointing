from typing import Any
import pickle
from checkpointing.hash._typing import Hash


def hash_bytes(hash_base: Hash, bytes_: bytes) -> Hash:
    """
    Hash the bytes with the given algorithm.
    The algorithm must be a valid value supported by `hashlib`, and must be provided as a keyword argument.
    If it's not specified, use the default in the global configuration (`defaults["hash.algorithm"]`)

    >>> res = hash_bytes(b'abc', b'def', algorithm="md5")
    >>> ref = hashlib.new("md5").update(b'abc').update(b'def').hexdigest()
    >>> res == ref
    True
    """

    hash_base.update(bytes_)
    return hash_base


def hash_object(hash_base: Hash, obj: Any, pickle_protocol=pickle.DEFAULT_PROTOCOL) -> Hash:
    """
    Hash the given object by getting it's binary representation as if it gets dumped with pickle,
    and hash the `bytes` object with the given algorithm.

    Args:
        obj: the object to hash
        algorithm: the hash algorithm to use
        pickle_protocol: the pickle protocol to use
    """

    bytes_ = pickle.dumps(obj, protocol=pickle_protocol)
    return hash_bytes(hash_base, bytes_)
