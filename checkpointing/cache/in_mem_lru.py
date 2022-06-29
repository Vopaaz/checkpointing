from checkpointing.cache.base import CacheBase
from checkpointing._typing import ContextId, ReturnValue
from checkpointing.exceptions import CheckpointNotExist
from collections import OrderedDict


class InMemoryLRUCache(CacheBase):
    """
    An in-memory cache that has a maximum capacity. When the number of entries cached exceeds the `maxsize`,
    the Least Recently Used entry will be deleted so that this cache won't consume infinitely large memory.

    Note that:
    1. This is an in-memory cache so the results can't be shared between two executions of the program
    2. The retrieved value will be the same object every time, and will be the same as the saved value. This
       means that any change on the saved/retrieved object will affect the objects to be retrieved with the
       same context id later on.
    3. Using this cache with any identifier that considers the parameter values is an analog to the built-
       in `functools.lru_cache`. This module is mostly built for testing purpose, because the built-in function
       should be much faster and is thus recommended to use. However, this might be useful in some cases, For
       example, ignoring some parameters on purpose. In such case you could use a custom identifier together
       with this cache.
    4. If using in multiprocessing, this is not a shared memory object, so the cache will not be shared between
       multiple processes
    """

    def __init__(self, maxsize=None) -> None:
        """
        Args:
            maxsize: max size of this cache. If None, the size will be infinite
        """
        self.__maxsize = maxsize

        if self.__maxsize is None:
            self.__d = {}
        else:
            self.__d = OrderedDict()

    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        self.__d[context_id] = result

        if self.__maxsize is not None:
            self.__d.move_to_end(context_id)

            if len(self.__d) > self.__maxsize:
                self.__d.popitem(last=False)

    def retrieve(self, context_id: ContextId) -> ReturnValue:
        if context_id not in self.__d:
            raise CheckpointNotExist

        if self.__maxsize is not None:
            self.__d.move_to_end(context_id)

        return self.__d[context_id]
