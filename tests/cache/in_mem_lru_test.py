from checkpointing.cache.in_mem_lru import InMemoryLRUCache
from checkpointing.exceptions import CheckpointNotExist
from nose.tools import assert_raises

def test_lru_basic_functionality():
    cache = InMemoryLRUCache()
    cache.save(0, 1)
    assert cache.retrieve(0) == 1

def test_lru_maxsize_works():
    cache = InMemoryLRUCache(2)

    cache.save(0, 0)
    assert cache.retrieve(0) == 0
    assert_raises(CheckpointNotExist, lambda: cache.retrieve(1))

    cache.save(1, 1)
    assert cache.retrieve(0) == 0
    assert cache.retrieve(1) == 1
    assert_raises(CheckpointNotExist, lambda: cache.retrieve(2))

    cache.save(2, 2)
    assert cache.retrieve(1) == 1
    assert cache.retrieve(2) == 2
    assert_raises(CheckpointNotExist, lambda: cache.retrieve(0))

    cache.retrieve(1) # Let 2 be the least recently used
    cache.save(3, 3)
    assert_raises(CheckpointNotExist, lambda: cache.retrieve(2))