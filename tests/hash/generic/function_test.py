from checkpointing.hash import hash_anything


def bar(x):
    return x

def foo():
    return 0


def test_different_function_hashes_differently():
    assert hash_anything(bar) != hash_anything(foo)


def test_same_function_hashes_the_same():
    assert hash_anything(bar) == hash_anything(bar)

# changing function code is not testable in unit tests
