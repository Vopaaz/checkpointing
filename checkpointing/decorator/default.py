from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.decorator.func_call.identifier import FuncCallHashIdentifier
from checkpointing.cache import PickleFileCache


def checkpoint(directory: str = None, error: str = "warn") -> DecoratorCheckpoint:
    """
    Alias for a default decorator checkpoint, which hashes the function code and parameter values,
    and save the return value as pickle files in a given directory.

    Args:
        directory: the directory used for saving the results. If None, use the global default
                    (`defaults["cache.filesystem.directory]`)
        error: the behavior when retrieval or saving raises unexpected exceptions. Possible values are:
                - `"raise"`, the exception will be raised.
                - `"warn"`, a warning will be issued to inform that the checkpointing task has failed.
                    But the user function will be invoked and executed as if it wasn't checkpointed.
                - `"ignore"`, the exception will be ignored and the user function will be invoked and executed normally.
    """

    identifier = FuncCallHashIdentifier()
    cache = PickleFileCache(directory)
    cp = DecoratorCheckpoint(identifier, cache, error)

    return cp
