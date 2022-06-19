from typing import Any
import pickle
from checkpointing.hash._typing import Hash


def hash_bytes(hash_base: Hash, bytes_: bytes) -> Hash:
    hash_base.update(bytes_)
    return hash_base


def hash_object(hash_base: Hash, obj: Any, pickle_protocol=pickle.DEFAULT_PROTOCOL) -> Hash:
    bytes_ = pickle.dumps(obj, protocol=pickle_protocol)
    return hash_bytes(hash_base, bytes_)
