from io import IOBase
import pickle
from typing import Any
from checkpointing.config import defaults

try:
    import pickle5
except ImportError:
    pass


def get_pickle_module(protocol: int):
    """
    Returns:
        built-in pickle module if the given protocol is supported.
        Otherwise check if the protocol = 5, if so, use pickle5.
    """

    if protocol <= pickle.HIGHEST_PROTOCOL:
        return pickle

    elif protocol == 5:
        return pickle5

    else:
        raise RuntimeError(f"pickle protocol {protocol} is not supported")


def dump(obj: Any, file: IOBase, protocol: int) -> None:
    return get_pickle_module(protocol).dump(obj, file, protocol)


def load(file: IOBase, protocol: int) -> Any:
    return get_pickle_module(protocol).load(file)
