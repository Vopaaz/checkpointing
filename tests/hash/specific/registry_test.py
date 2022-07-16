from checkpointing.hash.specific import register_hasher, hashable_with_specific, hash_with_specific
from checkpointing.exceptions import HashFailedError
from pytest import raises


class FooForRegistryTesting:
    def __init__(self) -> None:
        self.x = 0


def foo_for_registry_testing_hasher(obj: FooForRegistryTesting) -> bytes:
    return bytes([obj.x])


def test_register_new_hasher_for_class():

    register_hasher(FooForRegistryTesting, foo_for_registry_testing_hasher)
    assert hash_with_specific(FooForRegistryTesting()) == bytes([0])


class BarForRegistryTesting:
    pass


def test_hash_unregistered_throws_error():
    with raises(HashFailedError):
        hash_with_specific(BarForRegistryTesting())
