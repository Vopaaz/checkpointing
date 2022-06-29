from abc import ABC, abstractmethod
from checkpointing.decorator.func_call.context import Context
from checkpointing._typing import ContextId


class FuncCallIdentifierBase(ABC):
    """
    Base class for function call identifiers.
    """

    @abstractmethod
    def identify(self, context: Context) -> ContextId:
        """
        Args:
            context: context of a function call

        Returns:
            a unique identifier of this function call, name it `ContextId`.

            Any change in the `context` that could result in a different return value
            of a function call should be differentiable in the returned `ContextId`.
        """
        pass
