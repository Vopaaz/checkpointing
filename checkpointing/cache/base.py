from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from checkpointing.decorator.func_call._typing import ContextId, ReturnValue
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

    def thread_synchronized(self) -> ThreadSafeCache:
        """
        Returns:
            A thread-safe version of this cache - multiple threads won't attempt saving/retrieval concurrently.
        """
        return ThreadSafeCache(self)

    def process_synchronized(self) -> ProcessSafeCache:
        """
        Returns:
            A process-safe version of this cache - multiple processes won't attempt saving/retrieval concurrently.
        """
        return ProcessSafeCache(self)


CacheSubclass = TypeVar("CacheSubclass", bound=CacheBase)


class ConcurrentSafeCache(CacheBase, Generic[CacheSubclass]):
    lock: Union[ThreadLock, ProcessLock]

    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        with self.lock:
            self._cache.save(context_id, result)

    def retrieve(self, context_id: ContextId) -> ReturnValue:
        with self.lock:
            return self._cache.retrieve(context_id)


class ThreadSafeCache(ConcurrentSafeCache):
    """
    Wrapper around a given cache object that makes it's `save` and `retrieve` method synchronized for multithreading.
    """

    def __init__(self, cache: CacheSubclass) -> None:
        """
        Args:
            cache: the cache object to be made as thread safe
        """
        self._cache = cache
        self.lock = ThreadLock()


class ProcessSafeCache(CacheBase, Generic[CacheSubclass]):
    """
    Wrapper around a given cache object that makes it's `save` and `retrieve` method synchronized for multiprocessing.
    """

    def __init__(self, cache: CacheSubclass) -> None:
        """
        Args:
            cache: the cache object to be made as "process safe"
        """
        self.__cache = cache
        self.lock = ProcessLock()
