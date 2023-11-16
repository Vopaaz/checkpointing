from io import IOBase
import pickle
from typing import Any


def dump(obj: Any, file: IOBase, protocol: int) -> None:
    return pickle.dump(obj, file, protocol)


def load(file: IOBase, protocol: int) -> Any:
    return pickle.load(file)
