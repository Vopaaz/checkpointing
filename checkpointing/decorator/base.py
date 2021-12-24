import inspect
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Dict, Generic, List, Tuple, TypeVar
from warnings import warn

from checkpointing.exceptions import CheckpointNotExist, ExpensiveOverheadWarning, CheckpointFailedWarning
from checkpointing.util.timing import Timer, timed_run
from checkpointing.decorator.typing import ReturnValue, Identifier
from checkpointing.decorator.context import Context


class DecoratorCheckpoint(ABC, Generic[ReturnValue]):
    """The base class for any decorator checkpoints."""

    def __init__(self, error: str = "warn") -> None:
        """
        Args:
            error: the behavior when retrieval or saving raises unexpected exceptions
                (exceptions other than checkpointing.CheckpointNotExist).
                Could be:
                - `"raise"`, the exception will be raised.
                - `"warn"`, a warning will be issued to inform that the checkpointing task has failed.
                    But the user function will be invoked and executed as if it wasn't checkpointed.
                - `"ignore"`, the exception will be ignored and the user function will be invoked and executed normally.
        """

        self.__error: str = error
        """The behavior when identification, saving or retrieval raises unexpected exceptions."""

        self.__context: Context = None
        """The context of the latest function call"""

        self.__validate_params()

    def __validate_params(self):
        error = ["raise", "warn", "ignore"]
        if self.__error not in error:
            raise ValueError(f"Invalid argument value for error: {self.__error}, must be one of {error}")

    def __call__(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        """Magic method invoked when used as a decorator."""

        @wraps(func)
        def inner(*args, **kwargs) -> ReturnValue:
            self.__context = Context(func, args, kwargs)

            retrieve_success, res, retrieve_time = self.__timed_safe_retrieve()
            if retrieve_success:
                return res
            else:
                res, run_time = timed_run(func, args, kwargs)
                save_time = self.__timed_safe_save(res)
                self.__warn_if_more_expensive(retrieve_time + save_time, run_time)
            return res

        return inner

    def __warn_if_more_expensive(self, checkpoint_time: float, run_time: float) -> None:
        """
        Warn the user if retrieval takes longer than running the function.

        Args:
            checkpoint_time: time for retrieving and saving the cached result
            run_time: time for running the function
        """
        if checkpoint_time > run_time:
            warn(
                f"The overhead for checkpointing '{self.__context.function_name}' could possibly take more time than the function call itself "
                f"({checkpoint_time:.2f}s > {run_time:.2f}s). "
                "Consider optimize the checkpoint or just remove it, and let the function execute every time.",
                category=ExpensiveOverheadWarning,
                stacklevel=3,
            )

    @abstractmethod
    def retrieve(self, context: Context) -> ReturnValue:
        """
        Retrieve the data based on the function call context.
        If the there is no corresponding previously saved results, raise a `checkpointing.CheckpointNotExist`.

        Args:
            context: Context of the function call

        Returns:
            The retrieved return value of the function call.
        """
        pass

    def _call_retrieve(self) -> ReturnValue:
        """
        Call `self.retrieve()` with correct parameters.

        Overwrite this method to create abstract subclasses that needs different parameters for retrieving the result.
        """
        return self.retrieve(self.__context)

    def __timed_safe_retrieve(self) -> Tuple[bool, ReturnValue, float]:
        """
        Retrive the cached result, tracking the time and capturing any error,
        dealing with them according to the level specified by `self.__error`

        Returns:
            A tuple of three elements:
            - bool: whether the retrival succeeds or not
            - ReturnValue: the extracted return value, if successful, otherwise None
            - float: the time (seconds) it takes to retrieve the result
        """

        timer = Timer().start()
        try:
            res = self._call_retrieve()
            return True, res, timer.time
        except CheckpointNotExist:
            return False, None, timer.time
        except Exception as e:
            self.__handle_unexpected_error(e)
            return False, None, timer.time

    def __handle_unexpected_error(self, error: Exception):
        """
        Handle the unexpected error according to the level specified by `self.__error`.

        Args:
            error: the raised exception. Note that checkpointing.exceptions.CheckpointNotExist should NOT be handled by this method.
                    It should be dealt within the saving/retrieving methods.
        """
        if self.__error == "raise":
            raise error
        elif self.__error == "warn":
            warn(
                f"Checkpointing for {self.__context.function_name} failed because of the following error: {str(error)}. "
                "The function is called to compute the return value.",
                CheckpointFailedWarning,
            )
        else:  # self.__error == "ignore"
            pass

    @abstractmethod
    def save(self, context: Context, result: ReturnValue) -> None:
        """
        Save the result for the function call context.

        Args:
            context: Context of the function call
        """
        pass

    def _call_save(self, result: ReturnValue) -> None:
        """
        Call `self.save()` with correct parameters.

        Overwrite this method to create abstract subclasses that needs different parameters for saving the result.
        """
        return self.save(self.__context, result)

    def __timed_safe_save(self, result: ReturnValue) -> float:
        """
        Save the result, tracking the time and capturing any error,
        dealing with them according to the level specified by `self.__error`

        Returns:
            the time (seconds) it takes to save the result
        """

        timer = Timer().start()
        try:
            self._call_save(result)
        except Exception as e:
            self.__handle_unexpected_error(e)

        return timer.time


class HashDecoratorCheckpoint(DecoratorCheckpoint, Generic[Identifier]):
    """
    Checkpoint that (conceptually) hash the context to a unique identifier,
    and use the identifier for the retrieval and saving.
    """

    @abstractmethod
    def hash(self, context: Context) -> Identifier:
        """
        Hash the function call context into a unique identifier.
        The identifier should encode any information that determines what the return value would be.

        Args:
            context: function call context

        Returns:
            A unique identifier for the function call.
            This will be used to retrive/save the function call result.
        """
        pass

    @abstractmethod
    def retrieve(self, identifier: Identifier) -> ReturnValue:
        """
        Retrieve the data based on the identifier.
        If the there is no corresponding previously saved results, raise a `checkpointing.CheckpointNotExist`.

        Args:
            identifier: Identifier of the function call

        Returns:
            The retrieved return value of the function call.
        """
        pass

    def _call_retrieve(self) -> ReturnValue:
        """
        Call self.retrieve() with the identifier.
        """
        id = self.identify(self.__context)
        return self.retrieve(id)

    @abstractmethod
    def save(self, identifier: Identifier, result: ReturnValue) -> None:
        """
        Save the result of the function based on the identifier.

        Args:
            identifier: Identifier of the function call
            result: Return value of the function call
        """
        pass

    def _call_save(self, result: ReturnValue) -> None:
        """
        Call self.save() with the identifier
        """
        id = self.identify(self.__context)
        self.save(id, result)
