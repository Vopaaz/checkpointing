from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from checkpointing._typing import ContextId, ReturnValue
from checkpointing.exceptions import CheckpointNotExist

from threading import Lock as ThreadLock
from multiprocessing import Lock as ProcessLock


class CacheBase(ABC, Generic[ContextId, ReturnValue]):
    """
    The base class for Cache.

    To implement a concrete Cache class, you need to implement the following abstract methods:
    - `save(self, context_id: ContextId, result: ReturnValue) -> None`
    - `retrieve(self, context: Context) -> ReturnValue`
    """

    @abstractmethod
    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        """
        Save the result with the given context id.

        Args:
            context_id: identifier of the function call context
            result: return value of the function call
        """
        pass

    @abstractmethod
    def retrieve(self, context_id: ContextId) -> ReturnValue:
        """
        Retrieve the function return value with the given context id.
        If there is no cached results for the context_id, throws a checkpointing.exceptions.CheckpointNotExist

        Args:
            context_id: identifier of the function call context

        Returns:
            The return value of the function that corresponds to this context id
        """
        pass

    def synchronize_with(self, lock) -> SynchronizedCache:
        """
        Returns:
            A process-safe version of this cache - multiple processes won't attempt saving/retrieval concurrently.
        """
        return SynchronizedCache(self, lock)


CacheSubclass = TypeVar("CacheSubclass", bound=CacheBase)


# Exclude this class from the coverage report because nosetests have weird behavior in multiprocessing
class SynchronizedCache(CacheBase, Generic[CacheSubclass]): # pragma: no cover
    """
    Base class for synchronized cache. In the constructor of a concrete subclass,
    a `self.lock` attribute should be assigned as a thread/process lock, or any analog of such synchronization locks.
    """

    def __init__(self, cache, lock) -> None:
        self.__cache = cache
        self.__lock = lock

    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        with self.__lock:
            self.__cache.save(context_id, result)

    def retrieve(self, context_id: ContextId) -> ReturnValue:
        with self.__lock:
            return self.__cache.retrieve(context_id)
