from typing import Any
import dill
from checkpointing.hash._typing import Hash
from types import ModuleType, FunctionType
import pathlib
import inspect
from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from checkpointing.exceptions import HashFailedError
from types import GeneratorType
import ast


def hash_bytes(hash_base: Hash, bytes_: bytes) -> Hash:
    hash_base.update(bytes_)
    return hash_base


def hash_string(hash_base: Hash, s: str) -> Hash:
    bytes = s.encode("utf-8")
    return hash_bytes(hash_base, bytes)


def hash_with_dill(hash_base: Hash, obj: Any, pickle_protocol: int):
    bytes_ = dill.dumps(obj, protocol=pickle_protocol, byref=True, recurse=False)
    return hash_bytes(hash_base, bytes_)


def hash_generator(hash_base: Hash, generator: GeneratorType):
    return hash_string(generator.__qualname__)


def hash_generic(hash_base: Hash, obj: Any, pickle_protocol: int):
    try:
        return hash_with_dill(hash_base, obj, pickle_protocol)
    except:
        pass

    if inspect.isgenerator(obj):
        return hash_generator(hash_base, obj)

    raise HashFailedError(f"Cannot hash object of type: {type(obj)}")
