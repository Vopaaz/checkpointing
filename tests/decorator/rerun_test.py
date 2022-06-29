from checkpointing.decorator import checkpoint
from tests.testutils import rmdir_func, tmpdir, mkdir_func
from nose.tools import with_setup, raises


counter = 0  # Global counter


@checkpoint(directory=tmpdir)
def foo(a):
    global counter
    counter += 1
    return a


@with_setup(setup=mkdir_func, teardown=rmdir_func)
def test_rerun_is_added_and_works():
    global counter
    counter = 0

    foo(0)
    assert counter == 1

    foo(0)
    assert counter == 1  # Basic test that cache works

    foo.rerun(0)
    assert counter == 2


@with_setup(setup=mkdir_func, teardown=rmdir_func)
def test_rerun_pass_parameters_and_returns_correctly():
    assert foo.rerun(1) == 1
    assert foo.rerun(a=2) == 2


@with_setup(setup=mkdir_func, teardown=rmdir_func)
@raises(TypeError)
def test_rerun_does_not_accept_wrong_args():
    foo.rerun(1, 2)


@with_setup(setup=mkdir_func, teardown=rmdir_func)
@raises(TypeError)
def test_rerun_does_not_accept_wrong_kwargs():
    foo.rerun(c=3)
