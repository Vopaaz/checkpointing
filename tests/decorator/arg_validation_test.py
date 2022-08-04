from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.identifier.func_call import AutoFuncCallIdentifier, FuncCallIdentifierBase
from checkpointing.cache import InMemoryLRUCache
from pytest import raises

def test_invalid_identifier_throws_error():
    with raises(ValueError):
        DecoratorCheckpoint(0, InMemoryLRUCache())

    
def test_invalid_cache_throws_error():
    with raises(ValueError):
        DecoratorCheckpoint(AutoFuncCallIdentifier(), 0)

def test_invalid_error_level_throws_error():
    with raises(ValueError):
        DecoratorCheckpoint(AutoFuncCallIdentifier(), InMemoryLRUCache(), "hello")
