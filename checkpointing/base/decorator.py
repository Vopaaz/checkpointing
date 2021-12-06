from typing import Callable, TypeVar, List, Dict
from abc import abstractmethod, ABC
from checkpointing.base.exceptions import CheckpointNotExist

Identifier = TypeVar("Identifier")
"""
Object that uniquely identifies the parameters and dependencies of a function call
"""

ReturnValue = TypeVar("ReturnValue")
"""
Return value of the function
"""


class DecoratorCheckpoint(ABC):
    """The base class for any decorator checkpoints."""

    def __init__(self, error: str = "warn") -> None:
        """
        Args:
            error: the behavior when identification, saving, or retrieval raises unexpected exceptions.
                Could be:
                - `"raise"`, the exception will be raised.
                - `"warn"`, a warning will be issued to inform that the checkpointing task has failed.
                    But the user function will be invoked and executed as if it wasn't checkpointed.
                - `"ignore"`, the exception will be ignored and the user function will be invoked and executed normally.
        """

        self.args: List = []
        """Arguments in the latest function call"""

        self.kwargs: Dict = {}
        """Keyword arguments in the latest function call"""

        self.func: Callable[..., ReturnValue] = None
        """Function to be decorated"""

        self.error: str = error
        """The behavior when identification, saving or retrieval raises unexpected exceptions."""

    def __call__(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        """Magic method invoked when used as a decorator."""

        self.func = func

        def inner(*args, **kwargs) -> ReturnValue:
            self.args = args
            self.kwargs = kwargs

            try:
                id = self.identify()
            except Exception as e:
                pass
            
            try:
                res = self.retrieve(id)
            except CheckpointNotExist:
                res = func(*args, **kwargs)
                self.save(res, id)

            return res

        return inner

    @abstractmethod
    def identify(self) -> Identifier:
        pass

    @abstractmethod
    def save(self, id: Identifier, result: ReturnValue) -> None:
        pass

    @abstractmethod
    def retrieve(self, id: Identifier) -> ReturnValue:
        pass


class BuiltinDecoratorCheckpoint(DecoratorCheckpoint):
    def __init__(self) -> None:
        pass
