from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.decorator.func_call.identifier import AutoHashIdentifier, FuncCallIdentifierBase
from checkpointing.cache import InMemoryLRUCache
from pytest import raises

def test_invalid_identifier_throws_error():
    with raises(ValueError):
        DecoratorCheckpoint(0, InMemoryLRUCache())

    
def test_invalid_cache_throws_error():
    with raises(ValueError):
        DecoratorCheckpoint(AutoHashIdentifier(), 0)

def test_invalid_error_level_throws_error():
    with raises(ValueError):
        DecoratorCheckpoint(AutoHashIdentifier(), InMemoryLRUCache(), "hello")
