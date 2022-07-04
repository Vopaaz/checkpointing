import pathlib
import shutil
from pytest import fixture

tmpdir = pathlib.Path(".checkpointing-unit-test-tmp")

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
