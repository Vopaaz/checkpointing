from typing import Any
from checkpointing.config import Config as config
import hashlib


def hash_bytes(*bytes_: bytes):
    hash_fn = hashlib.new(config.hash.algorithm)
    for byte in bytes_:
        hash_fn.update(byte)
    return hash_fn.hexdigest()


def hash_object(obj: Any):
    pass
