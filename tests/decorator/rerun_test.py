from checkpointing.decorator import checkpoint
from tests.testutils import tmpdir, mkdir_before, rmdir_after
from pytest import raises


counter = 0  # Global counter


@checkpoint(directory=tmpdir)
def foo(a):
    global counter
    counter += 1
    return a


def test_rerun_is_added_and_works(mkdir_before, rmdir_after):
    global counter
    counter = 0

    foo(0)
    assert counter == 1

    foo(0)
    assert counter == 1  # Basic test that cache works

    foo.rerun(0)
    assert counter == 2


def test_rerun_pass_parameters_and_returns_correctly(mkdir_before, rmdir_after):
    assert foo.rerun(1) == 1
    assert foo.rerun(a=2) == 2


def test_rerun_does_not_accept_wrong_args(mkdir_before, rmdir_after):
    with raises(TypeError):
        foo.rerun(1, 2)


def test_rerun_does_not_accept_wrong_kwargs(mkdir_before, rmdir_after):
    with raises(TypeError):
        foo.rerun(c=3)
