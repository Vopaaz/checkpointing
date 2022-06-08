from abc import ABC, abstractmethod
from typing import Generic
from checkpointing._typing import ContextId, ReturnValue
from checkpointing.exceptions import CheckpointNotExist


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
