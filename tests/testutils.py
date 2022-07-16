import pathlib
import shutil
from pytest import fixture
from checkpointing import defaults

tmpdir = pathlib.Path(defaults["cache.filesystem.directory"])


def rmdir_func():
    if tmpdir.exists():
        shutil.rmtree(tmpdir)


def mkdir_func():
    if not tmpdir.exists():
        tmpdir.mkdir()


@fixture
def rmdir_before():
    rmdir_func()
    yield


@fixture
def rmdir_after():
    yield
    rmdir_func()


@fixture
def mkdir_before():
    mkdir_func()
    yield

counter = 0

@fixture
def reset_counter():
    global counter
    counter = 0
    yield

def increment_counter():
    global counter
    counter += 1

def get_counter():
    return counter