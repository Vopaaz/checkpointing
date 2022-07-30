from checkpointing.hash.stream import HashStream
from checkpointing.hash.generic import hash_generic, hash_with_dill, hash_with_pickle, hash_string, hash_with_qualname
import inspect
import warnings
from checkpointing.exceptions import HashFailedWarning


def test_hash_with_dill_works():
    s1 = HashStream()
    s2 = HashStream()

    hash_with_dill(s1, 0, 5)
    hash_with_dill(s2, 0, 5)

    assert s1.hexdigest() == s2.hexdigest()


def test_hash_with_pickle_works():
    s1 = HashStream()
    s2 = HashStream()

    hash_with_pickle(s1, 0, 5)
    hash_with_pickle(s2, 0, 5)

    assert s1.hexdigest() == s2.hexdigest()


def test_hash_with_string_works():
    s1 = HashStream()
    s2 = HashStream()

    hash_string(s1, "0")
    hash_string(s2, "0")

    assert s1.hexdigest() == s2.hexdigest()


def test_hash_with_qualname_works():
    def foo():
        yield

    s1 = HashStream()
    s2 = HashStream()
    f1 = foo()
    f2 = foo()

    hash_with_qualname(s1, "generator", f1)
    hash_with_qualname(s2, "generator", f2)


def test_hash_generic_works():
    s1 = HashStream()
    s2 = HashStream()

    hash_generic(s1, 0, 5)
    hash_generic(s2, 0, 5)

    assert s1.hexdigest() == s2.hexdigest()


def test_unpicklable_object_does_not_throw_error():
    s1 = HashStream()
    f1 = inspect.currentframe()

    with warnings.catch_warnings(record=True):
        hash_generic(s1, f1, 5)
