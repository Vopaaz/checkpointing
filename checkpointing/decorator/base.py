from typing import Callable, TypeVar, List, Dict, Tuple, Union
from abc import abstractmethod, ABC
from checkpointing.decorator.exceptions import CheckpointNotExist
import inspect
from functools import wraps

ReturnValue = TypeVar("ReturnValue")
"""
Return value of the function
"""


class Context:
    """
    Context of the function call.
    """

    def __init__(self, args, kwargs, func) -> None:
        """
        Args:
            args: the non-keywords arguments of the function call
            kwargs: the keyword arguments of the function call
            func: the function object that is being called
        """

        self.__args: List = args
        """Arguments of the function call"""

        self.__kwargs: Dict = kwargs
        """Keyword arguments of the function call"""

        self.__func: Callable[..., ReturnValue] = func
        """Function called"""

    @property
    def arguments(self):
        signature = inspect.signature(self.__func)
        args = signature.bind(*self.__args, **self.__kwargs)
        args.apply_defaults()
        return args.arguments


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

        self.error: str = error
        """The behavior when identification, saving or retrieval raises unexpected exceptions."""

        self.__context: Context = None
        """The context of the latest function call"""

    def __call__(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        """Magic method invoked when used as a decorator."""

        @wraps(func)
        def inner(*args, **kwargs) -> ReturnValue:
            self.__context = Context(args=args, kwargs=kwargs, func=func)
            try:
                res = self.retrieve(self.__context)
            except CheckpointNotExist:
                res = func(*args, **kwargs)
                self.save(self.__context, res)
            return res

        return inner

    @property
    def context(self) -> Context:
        """The context of the latest function call"""
        return self.__context

    @abstractmethod
    def save(self, ctx: Context, result: ReturnValue) -> None:
        pass

    @abstractmethod
    def retrieve(self, ctx: Context) -> ReturnValue:
        pass
