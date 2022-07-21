from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Dict, Generic, List, Tuple, TypeVar
from types import FrameType
from warnings import warn

from checkpointing.exceptions import CheckpointNotExist, ExpensiveOverheadWarning, CheckpointFailedWarning, CheckpointFailedError
from checkpointing.util.timing import Timer, timed_run
from checkpointing._typing import ReturnValue, ContextId
from checkpointing.identifier.func_call.context import FuncCallContext
from checkpointing.identifier.func_call import FuncCallIdentifierBase
from checkpointing.logging import logger
from checkpointing.config import defaults
from checkpointing.cache import CacheBase
import inspect


class DecoratorCheckpoint(ABC, Generic[ReturnValue]):
    """The base class for any decorator checkpoint."""

    def __init__(self, identifier: FuncCallIdentifierBase, cache: CacheBase, on_error: str = None) -> None:
        """
        Args:
            identifier: the function call identifier that creates an ID for the function call context
            cache: the cache instance that saves and reads the return value with the given ID
            on_error: the behavior when retrieval or saving raises unexpected exceptions
                (exceptions other than checkpointing.CheckpointNotExist). Possible values are:
                - `"raise"`, the exception will be raised.
                - `"warn"`, a warning will be issued to inform that the checkpointing task has failed.
                    But the user function will be invoked and executed as if it wasn't checkpointed.
                - `"ignore"`, the exception will be ignored and the user function will be invoked and executed normally.
                If None, use the global default `checkpoint.on_error`.
        """

        self.__identifier = identifier
        """The function call identifier"""

        self.__cache = cache
        """The cache instance"""

        if on_error is None:
            on_error = defaults["checkpoint.on_error"]

        self.__on_error: str = on_error
        """The behavior when identification, saving or retrieval raises unexpected exceptions."""

        self.__definition_frame: FrameType = None

        self.__validate_params()

    def __validate_params(self):
        if not isinstance(self.__identifier, FuncCallIdentifierBase):
            raise ValueError(f"Invalid type for identifier: {type(self.__identifier)}")

        if not isinstance(self.__cache, CacheBase):
            raise ValueError(f"Invalid type for cache: {type(self.__cache)}")

        error = ["raise", "warn", "ignore"]
        if self.__on_error not in error:
            raise ValueError(f"Invalid argument value for error: {self.__on_error}, must be one of {error}")

    def __call__(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        """Magic method invoked when used as a decorator."""
        logger.debug(f"{self.__class__.__name__} created for {func.__qualname__}")

        current_frame = inspect.currentframe()
        self.__definition_frame = current_frame.f_back if current_frame is not None else None

        inner = self.__create_inner(func)

        self.__bind_rerun(func, inner)

        return inner

    def __get_context_and_id(self, func, args, kwargs):
        context = FuncCallContext(func, args, kwargs, self.__definition_frame)
        context_id = self.__identifier.identify(context)
        return context, context_id

    def __create_inner(self, func: Callable[..., ReturnValue]) -> Callable[..., ReturnValue]:
        @wraps(func)
        def inner(*args, **kwargs) -> ReturnValue:

            context, context_id = self.__get_context_and_id(func, args, kwargs)
            retrieve_success, res, retrieve_time = self.__timed_safe_retrieve(context, context_id)

            if retrieve_success:
                logger.info(f"Result of {context.qualified_name} with args {context.arguments} retrieved from cache")
                return res

            else:
                logger.info(f"Result of {context.qualified_name} with args {context.arguments} unavailable from cache")

                res, run_time = timed_run(func, *args, **kwargs)

                save_time = self.__timed_safe_save(context, context_id, res)

                self.__warn_if_more_expensive(context, retrieve_time + save_time, run_time)
                return res

        return inner

    def __bind_rerun(self, original_func: Callable[..., ReturnValue], inner_func: Callable[..., ReturnValue]) -> None:
        def rerun(*args, **kwargs) -> ReturnValue:
            context, context_id = self.__get_context_and_id(original_func, args, kwargs)

            logger.info(f"Forcing rerun of {original_func.__qualname__}(**{context.arguments})")

            res, run_time = timed_run(original_func, *args, **kwargs)

            save_time = self.__timed_safe_save(context, context_id, res)

            self.__warn_if_more_expensive(context, save_time, run_time)
            return res

        inner_func.rerun = rerun

    def __warn_if_more_expensive(self, context: FuncCallContext, checkpoint_time: float, run_time: float, tol: float = 0.1) -> None:
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
                f"The overhead for checkpointing '{context.full_name}' could possibly take more time than the function call itself "
                f"({checkpoint_time:.2f}s > {run_time:.2f}s). "
                "Consider optimize the checkpoint or just remove it, and let the function execute every time.",
                category=ExpensiveOverheadWarning,
            )

    def __timed_safe_retrieve(self, context: FuncCallContext, context_id: ContextId) -> Tuple[bool, ReturnValue, float]:
        """
        Retrieve the cached result, tracking the time and capturing any error,
        dealing with them according to the level specified by `self.__on_error`

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

    def __handle_unexpected_error(self, context: FuncCallContext, error: Exception):
        """
        Handle the unexpected error according to the level specified by `self.__on_error`.

        Args:
            error: the raised exception. Note that checkpointing.exceptions.CheckpointNotExist should NOT be handled by this method.
                    It should be dealt within the saving/retrieving methods.
        """
        if self.__on_error == "raise":
            raise CheckpointFailedError(f"Checkpointing for {context.full_name} failed because of the following error: {str(error)}", error)

        elif self.__on_error == "warn":
            warn(
                f"Checkpointing for {context.full_name} failed because of the following error: {str(error)}. "
                "The function is called to compute the return value.",
                CheckpointFailedWarning,
            )

        else:  # self.__on_error == "ignore"
            pass

    def __timed_safe_save(self, context: FuncCallContext, context_id: ContextId, result: ReturnValue) -> float:
        """
        Save the result, tracking the time and capturing any error,
        dealing with them according to the level specified by `self.__on_error`

        Returns:
            the time (seconds) it takes to save the result
        """

        timer = Timer().start()
        try:
            self.__cache.save(context_id, result)
            logger.info(f"Result of {context.qualified_name} with args {context.arguments} saved to cache")

        except Exception as e:
            self.__handle_unexpected_error(context, e)

        return timer.time
