from checkpointing.decorator.base import DecoratorCheckpoint
from checkpointing.decorator.func_call.identifier import AutoHashIdentifier, FuncCallIdentifierBase
from checkpointing.cache import InMemoryLRUCache
from nose.tools import raises

@raises(ValueError)
def test_invalid_identifier_throws_error():
    DecoratorCheckpoint(0, InMemoryLRUCache())

    
@raises(ValueError)
def test_invalid_cache_throws_error():
    DecoratorCheckpoint(AutoHashIdentifier(), 0)

    
@raises(ValueError)
def test_invalid_error_level_throws_error():
    DecoratorCheckpoint(AutoHashIdentifier(), InMemoryLRUCache(), "hello")
