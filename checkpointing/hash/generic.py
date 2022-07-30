import inspect
from types import FunctionType, GeneratorType, ModuleType
from typing import Any
from warnings import warn

import dill
from checkpointing.exceptions import HashFailedWarning
from checkpointing.hash.stream import HashStream
from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from checkpointing.util import pickle
from checkpointing.logging import logger


def hash_with_dill(stream: HashStream, obj: Any, pickle_protocol: int) -> None:
    dill.dump(
        obj,
        stream,
        # Although we ported pickle5 for python 3.7-, dill is not aware of it. Using protocol = 5 for dill will cause it to fail
        protocol=min(pickle_protocol, dill.HIGHEST_PROTOCOL),
        byref=True,
        recurse=False,
    )


def hash_with_pickle(stream: HashStream, obj: Any, pickle_protocol: int) -> None:
    pickle.dump(obj, stream, protocol=pickle_protocol)


def hash_string(stream: HashStream, s: str) -> None:
    bytes_ = s.encode("utf-8")
    stream.write(bytes_)


def hash_with_qualname(stream: HashStream, type_: str, obj: Any) -> None:
    hash_string(stream, f"{type_}::{obj.__qualname__}")


def hash_generic(stream: HashStream, obj: Any, pickle_protocol: int) -> None:

    for test, type_ in [
        (inspect.isgenerator, "generator"),
    ]:
        if test(obj):
            hash_with_qualname(stream, type_, obj)
            return

    for hasher in [hash_with_pickle, hash_with_dill]:
        try:
            hasher(stream, obj, pickle_protocol)
            return
        except:
            pass

    warn(
        f"No generic hasher found for object: {str(obj)} of type: {type(obj)}, using its __repr__ as hash value. "
        "This could lead to incorrect results",
        category=HashFailedWarning,
    )
    hash_string(stream, repr(obj))
