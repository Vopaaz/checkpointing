from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.identifier.func_call import AutoFuncCallIdentifier
from checkpointing.cache import PickleFileCache


def checkpoint(
    directory: str = None,
    on_error: str = "warn",
    cache_pickle_protocol: int = None,
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

        cache_pickle_protocol: the pickle protocol used by the cache to save results to the disk.
                              If None, use the global default `cache.pickle_protocol`

    Optionally user can directly decorate the function with `@checkpoint` (without parenthesis),
    this will cause the function to be passed in directly with the `directory` parameter.
    """

    # If true, the `directory` is actually the decorated function
    # and the actual `directory` is None
    used_without_parenthesis = callable(directory)

    identifier = AutoFuncCallIdentifier()
    cache = PickleFileCache(None if used_without_parenthesis else directory, cache_pickle_protocol)
    decorator = DecoratorCheckpoint(identifier, cache, on_error)

    return decorator(directory) if used_without_parenthesis else decorator
