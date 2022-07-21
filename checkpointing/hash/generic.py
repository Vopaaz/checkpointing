from typing import Any
import dill
from checkpointing.hash._typing import Hash
from types import ModuleType, FunctionType
import inspect
from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from checkpointing.exceptions import HashFailedWarning
from types import GeneratorType
from warnings import warn


def hash_string(s: str) -> bytes:
    bytes = s.encode("utf-8")
    return bytes


def hash_with_dill(obj: Any, pickle_protocol: int) -> bytes:
    return dill.dumps(obj, protocol=pickle_protocol, byref=True, recurse=False)


def hash_generator(generator: GeneratorType) -> bytes:
    return hash_string(generator.__qualname__)


def hash_generic(obj: Any, pickle_protocol: int):
    try:
        return hash_with_dill(obj, pickle_protocol)
    except:
        pass

    if inspect.isgenerator(obj):
        return hash_generator(obj)

    warn(
        f"No generic hasher found for object: {str(obj)} of type: {type(obj)}, using its direct string representation as hash value. "
        "This could lead to incorrect results",
        category=HashFailedWarning,
    )
    return hash_string(str(obj))
