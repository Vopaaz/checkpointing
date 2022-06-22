from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.exceptions import ExpensiveOverheadWarning, CheckpointFailedError, CheckpointFailedWarning
from checkpointing.cache import CacheBase, InMemoryLRUCache
from checkpointing import ContextId, ReturnValue, FuncCallHashIdentifier
from nose.tools import raises
import warnings
import time


class SlowCache(InMemoryLRUCache):
    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        time.sleep(0.5)
        return super().save(context_id, result)

    def retrieve(self, context_id: ContextId) -> ReturnValue:
        time.sleep(0.5)
        return super().retrieve(context_id)


class ErrorCache(InMemoryLRUCache):
    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        raise ValueError

    def retrieve(self, context_id: ContextId) -> ReturnValue:
        raise ValueError


slow_deco = DecoratorCheckpoint(FuncCallHashIdentifier(), SlowCache(), error="raise")
error_deco = DecoratorCheckpoint(FuncCallHashIdentifier(), ErrorCache(), error="raise")
warn_deco = DecoratorCheckpoint(FuncCallHashIdentifier(), ErrorCache(), error="warn")
ignore_deco = DecoratorCheckpoint(FuncCallHashIdentifier(), ErrorCache(), error="ignore")


@slow_deco
def slow_func():
    return 0


@error_deco
def error_func():
    return 0


@warn_deco
def warn_func():
    return 0


@ignore_deco
def ignore_func():
    return 0


def test_slow_decorator_gives_warning():  # which ignores any "error" parameters
    with warnings.catch_warnings(record=True) as w:
        assert slow_func() == 0
        assert len(w) == 1
        assert issubclass(w[-1].category, ExpensiveOverheadWarning)


@raises(CheckpointFailedError)
def test_error_decorator_throws_error():
    error_func()


def test_warn_decorator_gives_warning():
    with warnings.catch_warnings(record=True) as w:
        assert warn_func() == 0
        assert len(w) == 1
        assert issubclass(w[-1].category, CheckpointFailedWarning)


def test_ignore_decorator_ignores_error():
    with warnings.catch_warnings(record=True) as w:
        assert ignore_func() == 0
        assert len(w) == 0
