from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Dict, Generic, List, Tuple, TypeVar
from warnings import warn

from checkpointing.exceptions import CheckpointNotExist, ExpensiveOverheadWarning, CheckpointFailedWarning, CheckpointFailedError
from checkpointing.util.timing import Timer, timed_run
from checkpointing._typing import ReturnValue, ContextId
from checkpointing.decorator.func_call.context import Context
from checkpointing.decorator.func_call.identifier import FuncCallHashIdentifier, FuncCallIdentifierBase
from checkpointing.logging import logger

from checkpointing.cache import CacheBase, PickleFileCache


class DecoratorCheckpoint(ABC, Generic[ReturnValue]):
    """The base class for any decorator checkpoint."""

    def __init__(self, identifier: FuncCallIdentifierBase, cache: CacheBase, error: str = "warn") -> None:
        """
        Args:
            identifier: the function call identifier that creates an ID for the function call context
            cache: the cache instance that saves and reads the return value with the given ID
            error: the behavior when retrieval or saving raises unexpected exceptions
                (exceptions other than checkpointing.CheckpointNotExist). Possible values are:
                - `"raise"`, the exception will be raised.
                - `"warn"`, a warning will be issued to inform that the checkpointing task has failed.
                    But the user function will be invoked and executed as if it wasn't checkpointed.
                - `"ignore"`, the exception will be ignored and the user function will be invoked and executed normally.
        """

        self.__identifier = identifier
        """The function call identifier"""

        self.__cache = cache
        """The cache instance"""

        self.__error: str = error
        """The behavior when identification, saving or retrieval raises unexpected exceptions."""

        self.__validate_params()

    def __validate_params(self):
        if not isinstance(self.__identifier, FuncCallIdentifierBase):
            raise ValueError(f"Invalid type for identifier: {type(self.__identifier)}")

        if not isinstance(self.__cache, CacheBase):
            raise ValueError(f"Invalid type for cache: {type(self.__cache)}")

        error = ["raise", "warn", "ignore"]
        if self.__error not in error:
            raise ValueError(f"Invalid argument value for error: {self.__error}, must be one of {error}")

    def __call__(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        """Magic method invoked when used as a decorator."""
        logger.debug(f"{self.__class__.__name__} created for {func.__qualname__}")

        inner = self.__create_inner(func)

        self.__bind_rerun(func, inner)

        return inner

    def __create_inner(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        @wraps(func)
        def inner(*args, **kwargs) -> ReturnValue:

            context = Context(func, args, kwargs)
            context_id = self.__identifier.identify(context)

            retrieve_success, res, retrieve_time = self.__timed_safe_retrieve(context, context_id)

            if retrieve_success:
                logger.info(f"Result of {func.__qualname__}(**{context.arguments}) retrieved from cache")
                return res

            else:
                logger.info(f"Result of {func.__qualname__}(**{context.arguments}) unavailable from cache")

                res, run_time = timed_run(func, *args, **kwargs)

                save_time = self.__timed_safe_save(context, context_id, res)
                logger.info(f"Result of {func.__qualname__}(**{context.arguments}) saved to cache")

                self.__warn_if_more_expensive(context, retrieve_time + save_time, run_time)
                return res

        return inner

    def __bind_rerun(self, original_func: Callable[..., ReturnValue], inner_func: Callable[..., ReturnValue]) -> None:
        def rerun(*args, **kwargs) -> ReturnValue:
            context = Context(original_func, args, kwargs)
            context_id = self.__identifier.identify(context)

            logger.info(f"Forcing rerun of {original_func.__qualname__}(**{context.arguments})")

            res, run_time = timed_run(original_func, *args, **kwargs)

            save_time = self.__timed_safe_save(context, context_id, res)
            logger.info(f"Result of {original_func.__qualname__}(**{context.arguments}) saved to cache")

            self.__warn_if_more_expensive(context, save_time, run_time)
            return res

        inner_func.rerun = rerun

    def __warn_if_more_expensive(self, context: Context, checkpoint_time: float, run_time: float, tol: float = 0.1) -> None:
        """
        Warn the user if retrieval takes longer than running the function.

        Args:
            checkpoint_time: approximate time for retrieving and saving the cached result
            run_time: time for running the function
            tol: tolerance of the difference between checkpoint_time and run_time in seconds.
                Larger value indicates more tolerance of slow checkpointing, compared to actual function running, without raising an error.
                Negative value indicates checkpoint should take less time than function running to avoid raising an error.
        """

        if checkpoint_time > run_time + tol:
            warn(
                f"The overhead for checkpointing '{context.function_name}' could possibly take more time than the function call itself "
                f"({checkpoint_time:.2f}s > {run_time:.2f}s). "
                "Consider optimize the checkpoint or just remove it, and let the function execute every time.",
                category=ExpensiveOverheadWarning,
                stacklevel=3,
            )

    def __timed_safe_retrieve(self, context: Context, context_id: ContextId) -> Tuple[bool, ReturnValue, float]:
        """
        Retrieve the cached result, tracking the time and capturing any error,
        dealing with them according to the level specified by `self.__error`

        Returns:
            A tuple of three elements:
            - bool: whether the retrival succeeds or not
            - ReturnValue: the extracted return value, if successful, otherwise None
            - float: the time (seconds) it takes to retrieve the result
        """

        timer = Timer().start()
        try:
            res = self.__cache.retrieve(context_id)
            return True, res, timer.time

        except CheckpointNotExist:
            return False, None, timer.time

        except Exception as e:
            self.__handle_unexpected_error(context, e)
            return False, None, timer.time

    def __handle_unexpected_error(self, context: Context, error: Exception):
        """
        Handle the unexpected error according to the level specified by `self.__error`.

        Args:
            error: the raised exception. Note that checkpointing.exceptions.CheckpointNotExist should NOT be handled by this method.
                    It should be dealt within the saving/retrieving methods.
        """
        if self.__error == "raise":
            raise CheckpointFailedError(f"Checkpointing for {context.function_name} failed because of the following error: {str(error)}", error)

        elif self.__error == "warn":
            warn(
                f"Checkpointing for {context.function_name} failed because of the following error: {str(error)}. "
                "The function is called to compute the return value.",
                CheckpointFailedWarning,
            )

        else:  # self.__error == "ignore"
            pass

    def __timed_safe_save(self, context: Context, context_id: ContextId, result: ReturnValue) -> float:
        """
        Save the result, tracking the time and capturing any error,
        dealing with them according to the level specified by `self.__error`

        Returns:
            the time (seconds) it takes to save the result
        """

        timer = Timer().start()
        try:
            self.__cache.save(context_id, result)

        except Exception as e:
            self.__handle_unexpected_error(context, e)

        return timer.time
