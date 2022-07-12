from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.identifier.func_call import AutoHashIdentifier
from checkpointing.cache import PickleFileCache


def checkpoint(
    directory: str = None,
    on_error: str = "warn",
    algorithm: str = None,
    hash_pickle_protocol: int = None,
    save_pickle_protocol: int = None,
) -> DecoratorCheckpoint:
    """
    Alias for a default decorator checkpoint, which hashes the function code and parameter values,
    and save the return value as pickle files in a given directory.

    Args:
        directory: the directory used for saving the results. If None, use the global default
                   `cache.filesystem.directory`

        on_error: the behavior when retrieval or saving raises unexpected exceptions. Possible values are:
                - `"raise"`, the exception will be raised.
                - `"warn"`, a warning will be issued to inform that the checkpointing task has failed.
                    But the user function will be invoked and executed as if it wasn't checkpointed.
                - `"ignore"`, the exception will be ignored and the user function will be invoked and executed normally.
                If None, use the global default `checkpoint.on_error`

        algorithm: the hash algorithm used, if None, use the global default `hash.algorithm`

        hash_pickle_protocol: the pickle protocol used by the hasher. If None, use the global default
                              `hash.pickle_protocol`

        save_pickle_protocol: the pickle protocol used by the cache to save results to the disk.
                              If None, use the global default `cache.pickle_protocol`
    """

    identifier = AutoHashIdentifier(algorithm, hash_pickle_protocol)
    cache = PickleFileCache(directory, save_pickle_protocol)
    decorator = DecoratorCheckpoint(identifier, cache, on_error)

    return decorator
