from checkpointing.decorator import checkpoint
from tests.testutils import tmpdir, mkdir_before, rmdir_after, get_counter, increment_counter, reset_counter
from pytest import raises


@checkpoint(directory=tmpdir)
def foo(a):
    increment_counter()
    return get_counter()


def test_rerun_is_added_and_works(mkdir_before, rmdir_after, reset_counter):
    v0 = foo(0)
    assert v0 == 1

    v1 = foo(0)
    assert v1 == 1  # Basic test that cache works

    v2 = foo.rerun(0)
    assert v2 == 2


def test_rerun_pass_parameters_and_returns_correctly(mkdir_before, rmdir_after, reset_counter):
    assert foo.rerun(1) == 1
    assert foo.rerun(a=2) == 2


def test_rerun_does_not_accept_wrong_args(mkdir_before, rmdir_after):
    with raises(TypeError):
        foo.rerun(1, 2)


def test_rerun_does_not_accept_wrong_kwargs(mkdir_before, rmdir_after):
    with raises(TypeError):
        foo.rerun(c=3)
